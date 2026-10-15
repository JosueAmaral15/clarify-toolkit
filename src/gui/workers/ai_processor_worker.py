"""
AI Processor Worker - v2.9.114

Background worker for AI file processing tasks.
Extracted from ai_processor_dock.py for better modularity.
"""

# pylint: disable=missing-function-docstring  # run() is standard QThread method
# pylint: disable=broad-exception-caught  # Worker robustness
# pylint: disable=unnecessary-lambda  # Signal/slot pattern
# pylint: disable=too-many-instance-attributes  # Worker configuration
# pylint: disable=too-many-arguments  # Worker initialization

import os
from dataclasses import dataclass

from src.ai_processor import list_files_recursive, process_multiple_files
from src.core.filters import (
    MAX_CONDITIONS,
    MAX_CONDITION_TEXT_BYTES,
    Condition,
    filter_files_by_conditions,
)
from src.gui.base_dock import ProcessorWorkerBase

MAX_AI_TARGETS = 1_000
MAX_AI_PATH_BYTES = 4_096
MAX_AI_TOTAL_PATH_BYTES = 1024 * 1024
MAX_AI_EXTENSIONS = 128
MAX_AI_EXTENSION_BYTES = 4_096
MAX_AI_TOTAL_EXTENSION_BYTES = 64 * 1024
MAX_AI_DISCOVERED_FILES = 100_000
MAX_AI_CONDITION_CONTENT_BYTES = 4 * 1024 * 1024


@dataclass(frozen=True)
class AIPathTarget:
    """One GUI-snapshotted file or directory target."""

    path: str
    is_file: bool


@dataclass(frozen=True)
class AIConditionRequest:
    """Immutable condition state transferred to the worker."""

    field: str
    operator: str
    value: str
    scope_type: str
    scope_value: str
    case_sensitive: bool
    whole_word: bool
    use_regex: bool

    @classmethod
    def from_condition(cls, condition: Condition) -> "AIConditionRequest":
        return cls(
            field=condition.field,
            operator=condition.operator,
            value=condition.value,
            scope_type=condition.scope_type,
            scope_value=condition.scope_value,
            case_sensitive=condition.case_sensitive,
            whole_word=condition.whole_word,
            use_regex=condition.use_regex,
        )

    def to_condition(self) -> Condition:
        return Condition.from_mapping(
            {
                "field": self.field,
                "operator": self.operator,
                "value": self.value,
                "scope_type": self.scope_type,
                "scope_value": self.scope_value,
                "case_sensitive": self.case_sensitive,
                "whole_word": self.whole_word,
                "use_regex": self.use_regex,
            }
        )


@dataclass(frozen=True)
class AIFileDiscoveryPlan:
    """Bounded immutable discovery/filter state captured on the GUI thread."""

    targets: tuple[AIPathTarget, ...]
    extensions: tuple[str, ...]
    conditions: tuple[AIConditionRequest, ...]
    logic_operator: str
    filtering_enabled: bool

    def __post_init__(self):
        if not self.targets:
            raise ValueError("No file or directory paths provided")
        if len(self.targets) > MAX_AI_TARGETS:
            raise ValueError(f"At most {MAX_AI_TARGETS} paths can be processed")
        total_path_bytes = 0
        for target in self.targets:
            if not isinstance(target, AIPathTarget) or not target.path:
                raise ValueError("Each processing target must have a path")
            path_bytes = len(target.path.encode("utf-8"))
            if len(target.path) > MAX_AI_PATH_BYTES or path_bytes > MAX_AI_PATH_BYTES:
                raise ValueError("A processing path exceeds the 4 KiB limit")
            total_path_bytes += path_bytes
        if total_path_bytes > MAX_AI_TOTAL_PATH_BYTES:
            raise ValueError("Processing paths exceed the 1 MiB total limit")

        if len(self.extensions) > MAX_AI_EXTENSIONS:
            raise ValueError(f"At most {MAX_AI_EXTENSIONS} extensions can be used")
        total_extension_bytes = 0
        for extension in self.extensions:
            if not isinstance(extension, str):
                raise ValueError("Extensions must be text")
            extension_bytes = len(extension.encode("utf-8"))
            if len(extension) > MAX_AI_EXTENSION_BYTES or extension_bytes > MAX_AI_EXTENSION_BYTES:
                raise ValueError("An extension exceeds the 4 KiB limit")
            total_extension_bytes += extension_bytes
        if total_extension_bytes > MAX_AI_TOTAL_EXTENSION_BYTES:
            raise ValueError("Extensions exceed the 64 KiB total limit")

        if len(self.conditions) > MAX_CONDITIONS:
            raise ValueError(f"At most {MAX_CONDITIONS} conditions can be used")
        for condition in self.conditions:
            if not isinstance(condition, AIConditionRequest):
                raise ValueError("Conditions must be immutable condition requests")
            for text in (
                condition.field,
                condition.operator,
                condition.value,
                condition.scope_type,
                condition.scope_value,
            ):
                if not isinstance(text, str):
                    raise ValueError("Condition inputs must be text")
                if len(text) > MAX_CONDITION_TEXT_BYTES or len(text.encode("utf-8")) > MAX_CONDITION_TEXT_BYTES:
                    raise ValueError("Condition input exceeds the 64 KiB transfer limit")
        if self.logic_operator not in {"AND", "OR"}:
            raise ValueError("Condition logic must be AND or OR")

    def resolve(self, checkpoint):
        """Discover and filter files without reading GUI-owned state."""
        conditions = []
        if self.filtering_enabled:
            for condition in self.conditions:
                if not checkpoint():
                    return (), 0, 0
                conditions.append(condition.to_condition())

        files = []
        for target in self.targets:
            if not checkpoint():
                return tuple(files), len(files), 0
            if target.is_file:
                if not os.path.isfile(target.path):
                    raise ValueError(f"Not a file: {target.path}")
                files.append(target.path)
            else:
                if not os.path.isdir(target.path):
                    raise ValueError(f"Not a directory: {target.path}")
                remaining = MAX_AI_DISCOVERED_FILES - len(files)
                files.extend(
                    list_files_recursive(
                        target.path,
                        list(self.extensions),
                        checkpoint=checkpoint,
                        max_files=remaining,
                    )
                )
            if len(files) > MAX_AI_DISCOVERED_FILES:
                raise ValueError(f"File discovery exceeds the {MAX_AI_DISCOVERED_FILES}-file safety limit")

        if not checkpoint():
            return tuple(files), len(files), 0
        if not files:
            raise ValueError("No files found in any path")
        original_count = len(files)
        if not self.filtering_enabled or not conditions:
            return tuple(files), original_count, 0

        filtered = filter_files_by_conditions(
            files,
            tuple(conditions),
            self.logic_operator,
            checkpoint=checkpoint,
            max_content_bytes=MAX_AI_CONDITION_CONTENT_BYTES,
            strict_errors=True,
        )
        return tuple(filtered), original_count, original_count - len(filtered)


class AIProcessorWorker(ProcessorWorkerBase):
    """Background worker for AI file processing."""

    def __init__(
        self,
        discovery_plan,
        prompt,
        client,
        max_bytes,
        line_by_line,
        scope_filter_enabled=False,
        scope_start="",
        scope_end="",
        scope_start_regex=False,
        scope_start_case=False,
        scope_end_regex=False,
        scope_end_case=False,
        template_enabled=False,
    ):
        super().__init__()
        self.discovery_plan = discovery_plan
        self.prompt = prompt
        self.client = client
        self.max_bytes = max_bytes
        self.line_by_line = line_by_line
        self.scope_filter_enabled = scope_filter_enabled
        self.scope_start = scope_start
        self.scope_end = scope_end
        self.scope_start_regex = scope_start_regex
        self.scope_start_case = scope_start_case
        self.scope_end_regex = scope_end_regex
        self.scope_end_case = scope_end_case
        self.template_enabled = template_enabled

    def run(self):
        try:
            self.emit_progress("[Preparation] Discovering and filtering files...")
            files, original_count, filtered_out = self.discovery_plan.resolve(lambda: not self.check_interrupt())
            if self.check_interrupt():
                self.emit_progress("⚠️ Processing interrupted by user")
                self.emit_success([])
                return
            if not files:
                raise ValueError(f"All {original_count} file(s) were filtered out by advanced conditions")
            if filtered_out:
                self.emit_progress(
                    f"[Preparation] Filtering: {len(files)} of {original_count} file(s) "
                    f"({filtered_out} filtered out)"
                )
            else:
                self.emit_progress(f"[Preparation] Processing {len(files)} file(s) (no filters applied)")
            responses = process_multiple_files(
                files,
                self.prompt,
                self.client,
                self.max_bytes,
                self.line_by_line,
                progress_callback=lambda msg: self.emit_progress(msg),
                interrupt_check=lambda: self.check_interrupt(),
                scope_filter_enabled=self.scope_filter_enabled,
                scope_start=self.scope_start,
                scope_end=self.scope_end,
                scope_start_regex=self.scope_start_regex,
                scope_start_case=self.scope_start_case,
                scope_end_regex=self.scope_end_regex,
                scope_end_case=self.scope_end_case,
                template_enabled=self.template_enabled,
            )
            self.emit_success(responses)
        except Exception as e:
            self.emit_error(str(e))
