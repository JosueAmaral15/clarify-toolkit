# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
# pylint: disable=broad-exception-caught  # GUI must handle all exceptions gracefully
# pylint: disable=import-outside-toplevel  # Avoid circular imports
"""
Batch Manager for Set Operations
Manages batch execution of multiple set operations in pipeline.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.102
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from PySide6.QtCore import QThread, Signal


class BatchStep:
    """
    Represents a single step in batch pipeline.

    Attributes:
        operation: Operation type ('intersection', 'union', 'difference', 'symmetric_difference')
        file_a_source: Source for File A ('file_path' or 'previous_result')
        file_a_path: File path if file_a_source is 'file_path'
        file_b_path: File path for File B
        comparison_mode: Comparison mode ('key_value', 'full_path_value', 'key_only')
        options: Dict with ignore_case_keys, ignore_case_values, skip_empty, arrays_ignore_order
        description: Human-readable description
    """

    def __init__(self, operation: str, file_a_source: str, file_a_path: str,  # pylint: disable=too-many-positional-arguments
                 file_b_path: str, comparison_mode: str = 'key_value',
                 options: Dict[str, bool] = None, description: str = ""):
        """Initialize BatchStep."""
        self.operation = operation
        self.file_a_source = file_a_source  # 'file_path' or 'previous_result'
        self.file_a_path = file_a_path
        self.file_b_path = file_b_path
        self.comparison_mode = comparison_mode
        self.options = options or {}
        self.description = description

        # Execution state
        self.status = 'pending'  # 'pending', 'running', 'completed', 'failed'
        self.result = None
        self.result_count = 0
        self.error_message = ""
        self.execution_time = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'operation': self.operation,
            'file_a_source': self.file_a_source,
            'file_a_path': self.file_a_path,
            'file_b_path': self.file_b_path,
            'comparison_mode': self.comparison_mode,
            'options': self.options,
            'description': self.description
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BatchStep':
        """Create BatchStep from dict."""
        return BatchStep(
            operation=data['operation'],
            file_a_source=data['file_a_source'],
            file_a_path=data['file_a_path'],
            file_b_path=data['file_b_path'],
            comparison_mode=data.get('comparison_mode', 'key_value'),
            options=data.get('options', {}),
            description=data.get('description', '')
        )


class BatchJob:
    """
    Represents a batch job with multiple steps (named pipeline).

    Attributes:
        name: Job name
        steps: List of BatchStep
        save_intermediate: Whether to save intermediate results to folder
        output_folder: Folder to save intermediate results (if save_intermediate is True)
    """

    def __init__(self, name: str, steps: List[BatchStep] = None,
                 save_intermediate: bool = False, output_folder: str = ""):
        """Initialize BatchJob."""
        self.name = name
        self.steps = steps or []
        self.save_intermediate = save_intermediate
        self.output_folder = output_folder
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_step(self, step: BatchStep):
        """Add step to batch."""
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            'name': self.name,
            'steps': [step.to_dict() for step in self.steps],
            'save_intermediate': self.save_intermediate,
            'output_folder': self.output_folder,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BatchJob':
        """Create BatchJob from dict."""
        job = BatchJob(
            name=data['name'],
            save_intermediate=data.get('save_intermediate', False),
            output_folder=data.get('output_folder', '')
        )
        job.steps = [BatchStep.from_dict(s) for s in data.get('steps', [])]
        job.created_at = data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return job

    def save_to_file(self, file_path: str) -> bool:
        """Save batch job to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def load_from_file(file_path: str) -> Optional['BatchJob']:
        """Load batch job from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return BatchJob.from_dict(data)
        except Exception:
            return None


class BatchExecutor(QThread):
    """
    Thread-based executor for batch jobs.

    Executes steps sequentially, emits progress signals, handles errors.

    Signals:
        step_started: Emitted when step starts (step_index, total_steps)
        step_completed: Emitted when step completes (step_index, result_count, execution_time)
        step_failed: Emitted when step fails (step_index, error_message)
        batch_completed: Emitted when entire batch completes successfully
        batch_failed: Emitted when batch aborts due to error (failed_step_index, error_message)
        progress_message: Emitted with status messages (message: str)
    """

    step_started = Signal(int, int)  # (step_index, total_steps)
    step_completed = Signal(int, int, float)  # (step_index, result_count, execution_time)
    step_failed = Signal(int, str)  # (step_index, error_message)
    batch_completed = Signal()
    batch_failed = Signal(int, str)  # (failed_step_index, error_message)
    progress_message = Signal(str)

    def __init__(self, batch_job: BatchJob):
        """Initialize BatchExecutor."""
        super().__init__()
        self.batch_job = batch_job
        self._is_cancelled = False

    def cancel(self):
        """Cancel batch execution."""
        self._is_cancelled = True

    def run(self):
        """Execute batch job (runs in background thread)."""
        from src.set_operations import intersection, union, difference, symmetric_difference

        total_steps = len(self.batch_job.steps)
        previous_result = None

        self.progress_message.emit(f"Starting batch: {self.batch_job.name} ({total_steps} steps)")

        for step_index, step in enumerate(self.batch_job.steps):
            if self._is_cancelled:
                self.progress_message.emit("Batch cancelled by user")
                return

            # Emit step started
            self.step_started.emit(step_index, total_steps)
            step.status = 'running'

            start_time = time.time()

            try:
                # Prepare File A (from previous result or file path)
                if step.file_a_source == 'previous_result':
                    if previous_result is None:
                        raise ValueError("No previous result available (step 1 must use file_path)")
                    file_a_data = previous_result
                    file_a_path = f"<previous_result_step_{step_index}>"
                else:
                    file_a_path = step.file_a_path
                    if not os.path.exists(file_a_path):
                        raise FileNotFoundError(f"File A not found: {file_a_path}")
                    with open(file_a_path, 'r', encoding='utf-8') as f:
                        file_a_data = json.load(f)

                # Load File B
                file_b_path = step.file_b_path
                if not os.path.exists(file_b_path):
                    raise FileNotFoundError(f"File B not found: {file_b_path}")
                with open(file_b_path, 'r', encoding='utf-8') as f:
                    file_b_data = json.load(f)

                # Execute operation
                if step.operation == 'intersection':
                    result = intersection([file_a_data, file_b_data], step.comparison_mode, **step.options)
                elif step.operation == 'union':
                    result = union([file_a_data, file_b_data], step.comparison_mode, **step.options)
                elif step.operation == 'difference':
                    result = difference([file_a_data, file_b_data], step.comparison_mode, **step.options)
                elif step.operation == 'symmetric_difference':
                    result = symmetric_difference(file_a_data, file_b_data, step.comparison_mode, **step.options)
                else:
                    raise ValueError(f"Unknown operation: {step.operation}")

                # Store result
                previous_result = result
                step.result = result
                step.result_count = len(result) if isinstance(result, (dict, list)) else 0
                step.status = 'completed'

                execution_time = time.time() - start_time
                step.execution_time = execution_time

                # Save intermediate result if enabled
                if self.batch_job.save_intermediate and self.batch_job.output_folder:
                    self._save_intermediate_result(step_index, result)

                # Emit step completed
                self.step_completed.emit(step_index, step.result_count, execution_time)
                self.progress_message.emit(f"Step {step_index + 1}/{total_steps} completed: {step.result_count} results")

            except Exception as e:
                # Handle error
                error_message = str(e)
                step.status = 'failed'
                step.error_message = error_message

                # Emit step failed
                self.step_failed.emit(step_index, error_message)
                self.progress_message.emit(f"Step {step_index + 1}/{total_steps} failed: {error_message}")

                # Abort batch (Stop Immediately strategy)
                self.batch_failed.emit(step_index, error_message)
                return

        # All steps completed successfully
        self.batch_completed.emit()
        self.progress_message.emit(f"Batch completed: {total_steps}/{total_steps} steps successful")

    def _save_intermediate_result(self, step_index: int, result: Any):
        """Save intermediate result to output folder."""
        try:
            output_folder = Path(self.batch_job.output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

            output_file = output_folder / f"step_{step_index + 1}_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception:
            # Silent fail for intermediate saves (not critical)
            pass


class BatchHistory:
    """
    Manages batch job history using QSettings.

    Stores last 10 batch executions for quick reuse.
    """

    MAX_HISTORY = 10

    def __init__(self):
        """Initialize BatchHistory."""
        from PySide6.QtCore import QSettings
        self.settings = QSettings("Clarify", "BatchHistory")

    def add_batch(self, batch_job: BatchJob):
        """Add batch job to history."""
        history = self.get_history()

        # Add to front
        history.insert(0, batch_job.to_dict())

        # Keep only MAX_HISTORY
        history = history[:self.MAX_HISTORY]

        # Save
        self.settings.setValue("batch_history", json.dumps(history))

    def get_history(self) -> List[Dict[str, Any]]:
        """Get batch history."""
        history_str = self.settings.value("batch_history", "[]")
        try:
            return json.loads(history_str)
        except Exception:
            return []

    def clear_history(self):
        """Clear batch history."""
        self.settings.remove("batch_history")
