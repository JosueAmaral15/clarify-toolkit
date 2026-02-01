"""
AI Processor Worker - v2.9.114

Background worker for AI file processing tasks.
Extracted from ai_processor_dock.py for better modularity.
"""

from src.gui.base_dock import ProcessorWorkerBase
from src.ai_processor import process_multiple_files


class AIProcessorWorker(ProcessorWorkerBase):
    """Background worker for AI file processing."""

    def __init__(self, files, prompt, client, max_bytes, line_by_line,
                 scope_filter_enabled=False, scope_start="", scope_end="",
                 scope_start_regex=False, scope_start_case=False,
                 scope_end_regex=False, scope_end_case=False,
                 template_enabled=False):
        super().__init__()
        self.files = files
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
            responses = process_multiple_files(
                self.files,
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
                template_enabled=self.template_enabled
            )
            self.emit_success(responses)
        except Exception as e:
            self.emit_error(str(e))
