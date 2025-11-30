"""
JSON Search Dock Widget

Provides UI for searching keys and values in JSON and TypeScript files.
"""

import os
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QCheckBox, QSpinBox, QComboBox, QHBoxLayout
from ..gui.base_dock import StandardToolDock, ProcessorWorkerBase
from ..json_search import ProjectIndexer, parse_composite_query, resolve_query, match_with_options


class JsonSearchWorker(ProcessorWorkerBase):
    """Background worker for JSON search."""
    
    def __init__(self, files, search_key, search_value, search_mode, case_sensitive, use_regex, max_results):
        super().__init__()
        self.files = files
        self.search_key = search_key
        self.search_value = search_value
        self.search_mode = search_mode
        self.case_sensitive = case_sensitive
        self.use_regex = use_regex
        self.max_results = max_results
    
    def run(self):
        try:
            # Create indexer and index files
            self.emit_progress(f"Indexing {len(self.files)} file(s)...")
            indexer = ProjectIndexer()
            
            for i, file_path in enumerate(self.files):
                if self.check_interrupt():
                    self.emit_progress("⚠️ Search interrupted")
                    break
                
                try:
                    indexer.index_file(file_path)
                    self.emit_progress(f"[{i+1}/{len(self.files)}] Indexed {os.path.basename(file_path)}")
                except Exception as e:
                    self.emit_progress(f"✗ Error indexing {os.path.basename(file_path)}: {str(e)}")
            
            # Search
            self.emit_progress("\n🔍 Searching...")
            query = self.search_key if self.search_key else self.search_value
            
            if not query:
                self.emit_error("No search query provided")
                return
            
            # Use resolve_query to find matches
            results = resolve_query(
                indexer.flat_index,
                query,
                self.case_sensitive,
                False,  # whole_word
                self.use_regex
            )
            
            # Limit results
            if self.max_results > 0 and len(results) > self.max_results:
                results = results[:self.max_results]
                self.emit_progress(f"⚠️ Limited to {self.max_results} results")
            
            self.emit_success(results)
            
        except Exception as e:
            self.emit_error(str(e))


class JsonSearchDock(StandardToolDock):
    """Dock widget for JSON search tool."""
    
    def __init__(self, parent=None):
        super().__init__("JSON Search", parent)
        self.worker = None
        self.last_results = []  # Store last search results for saving
    
    def _setup_ui(self):
        """Setup UI components."""
        grid = QGridLayout()
        
        # Search inputs
        grid.addWidget(QLabel("Search key:"), 0, 0)
        self.ed_search_key = QLineEdit()
        self.ed_search_key.setPlaceholderText("e.g., 'home.title' or leave empty")
        self.ed_search_key.setToolTip("Search for JSON keys using dot-path notation (e.g., 'user.profile.name')")
        grid.addWidget(self.ed_search_key, 0, 1, 1, 3)
        
        grid.addWidget(QLabel("Search value:"), 1, 0)
        self.ed_search_value = QLineEdit()
        self.ed_search_value.setPlaceholderText("e.g., 'Welcome' or leave empty")
        self.ed_search_value.setToolTip("Search for specific values in your JSON files (supports regex)")
        grid.addWidget(self.ed_search_value, 1, 1, 1, 3)
        
        # Filename filter (NEW - Task #6)
        grid.addWidget(QLabel("Filename filter:"), 2, 0)
        self.ed_filename = QLineEdit()
        self.ed_filename.setPlaceholderText("e.g., '*.config.ts' or 'filename:en' or leave empty")
        self.ed_filename.setToolTip(
            "Filter files by name:\n"
            "• Wildcards: '*.config.ts', 'en_*.json'\n"
            "• Prefix: 'filename:en' (matches en.ts, en-US.json, etc.)\n"
            "• Advanced: Use regex when 'Use regex' is checked"
        )
        grid.addWidget(self.ed_filename, 2, 1, 1, 3)
        
        # Search mode
        grid.addWidget(QLabel("Search mode:"), 3, 0)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Key and Value", "Key only", "Value only"])
        grid.addWidget(self.combo_mode, 3, 1, 1, 3)
        
        # File/directory input
        lbl_path, self.ed_path, self.btn_browse, self.chk_is_file = self.create_file_input(
            "Search path:",
            "File or directory to search"
        )
        grid.addWidget(lbl_path, 4, 0)
        grid.addWidget(self.ed_path, 4, 1, 1, 2)
        grid.addWidget(self.btn_browse, 4, 3)
        
        # Options
        self.chk_case = QCheckBox("Case sensitive")
        self.chk_regex = QCheckBox("Use regex")
        grid.addWidget(self.chk_is_file, 5, 0)
        grid.addWidget(self.chk_case, 5, 1)
        grid.addWidget(self.chk_regex, 5, 2)
        
        # Max results
        grid.addWidget(QLabel("Max results:"), 5, 3)
        self.spin_max = QSpinBox()
        self.spin_max.setRange(0, 10000)
        self.spin_max.setValue(1000)
        self.spin_max.setSpecialValueText("Unlimited")
        grid.addWidget(self.spin_max, 5, 4)
        
        self.layout.addLayout(grid)
        
        # Action buttons
        buttons = [
            ("Search", self._search),
            ("Interrupt", self._interrupt),
            ("Save Results", self._save_results),
            ("Clear", self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.btn_interrupt.setEnabled(False)
        self.btn_save_results.setEnabled(False)  # Disable until we have results
        self.layout.addLayout(btn_layout)
        
        # Results panel
        lbl_results, self.text_results = self.create_results_panel()
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.text_results)
        
        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        self.btn_browse.clicked.connect(self._browse)
        self._setup_enter_key_execution(self.ed_search_key, self.ed_search_value, self.ed_filename)
    
    def _browse(self):
        """Browse for file or directory."""
        self.browse_file_or_directory(
            self.ed_path,
            self.chk_is_file.isChecked(),
            "JSON/TS files (*.json *.ts *.js);;All files (*)"
        )
    
    def _get_files(self):
        """Get list of files to search."""
        import re
        import fnmatch
        
        path = self.ed_path.text().strip()
        valid, error = self.validate_file_path(path)
        if not valid:
            raise ValueError(error)
        
        # Get base file list
        if self.chk_is_file.isChecked():
            if not os.path.isfile(path):
                raise ValueError(f"Not a file: {path}")
            files = [path]
        else:
            if not os.path.isdir(path):
                raise ValueError(f"Not a directory: {path}")
            
            files = list_files_recursive(path, ['.json', '.ts', '.js'])
            if not files:
                raise ValueError(f"No JSON/TS files found in {path}")
        
        # Apply filename filter (Task #6)
        filename_filter = self.ed_filename.text().strip()
        if filename_filter:
            use_regex = self.chk_regex.isChecked()
            
            # Method 1: prefix "filename:" - matches files containing the text
            if filename_filter.startswith("filename:"):
                search_text = filename_filter[9:].strip()  # Remove "filename:" prefix
                files = [f for f in files if search_text in os.path.basename(f)]
            
            # Method 2: regex (when checkbox is enabled)
            elif use_regex:
                try:
                    pattern = re.compile(filename_filter)
                    files = [f for f in files if pattern.search(os.path.basename(f))]
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {e}")
            
            # Method 3: wildcards (default)
            else:
                files = [f for f in files if fnmatch.fnmatch(os.path.basename(f), filename_filter)]
            
            if not files:
                raise ValueError(f"No files match filename filter: {filename_filter}")
        
        return files
    
    def _search(self):
        """Start search process."""
        try:
            # Get search parameters
            search_key = self.ed_search_key.text().strip()
            search_value = self.ed_search_value.text().strip()
            
            if not search_key and not search_value:
                self.show_warning("No Search Terms", "Please enter a key or value to search for.")
                return
            
            # Get files
            files = self._get_files()
            
            # Get search mode
            mode_text = self.combo_mode.currentText()
            if mode_text == "Key only":
                search_mode = "key"
            elif mode_text == "Value only":
                search_mode = "value"
            else:
                search_mode = "both"
            
            # Start worker
            self.worker = JsonSearchWorker(
                files,
                search_key,
                search_value,
                search_mode,
                self.chk_case.isChecked(),
                self.chk_regex.isChecked(),
                self.spin_max.value()
            )
            self.worker.progress.connect(lambda msg: self.append_result(self.text_results, msg))
            self.worker.finished_ok.connect(self._on_finished)
            self.worker.failed.connect(self._on_failed)
            
            self.btn_search.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.clear_results(self.text_results)
            self.append_result(self.text_results, f"Searching in {len(files)} file(s)...\n")
            
            self.worker.start()
            
        except Exception as e:
            self.show_error("Search Error", str(e))
    
    def _interrupt(self):
        """Interrupt search."""
        if self.worker and self.worker.isRunning():
            self.worker.request_interrupt()
    
    def _on_finished(self, results):
        """Handle search completion."""
        from collections import Counter
        
        self.last_results = results  # Store results for saving
        
        self.append_result(self.text_results, f"\n{'='*60}")
        self.append_result(self.text_results, f"✅ Search complete! Found {len(results)} match(es).\n")
        
        if results:
            # Task #11 - Contagem de ocorrências
            # Count occurrences per file and per key
            file_counter = Counter()
            key_counter = Counter()
            
            for result in results:
                file_path = result.get('file', 'unknown')
                key = result.get('key', '')
                file_counter[os.path.basename(file_path)] += 1
                if key:
                    key_counter[key] += 1
            
            # Display occurrence statistics
            self.append_result(self.text_results, "\n📊 Occurrence Statistics:")
            self.append_result(self.text_results, f"Total occurrences: {len(results)}")
            self.append_result(self.text_results, f"Files with matches: {len(file_counter)}")
            
            # Top files by occurrence count
            if file_counter:
                self.append_result(self.text_results, "\nTop files by occurrences:")
                for filename, count in file_counter.most_common(5):
                    self.append_result(self.text_results, f"  • {filename}: {count} occurrence(s)")
            
            # Top keys by occurrence count
            if key_counter:
                self.append_result(self.text_results, "\nTop keys by occurrences:")
                for key, count in key_counter.most_common(5):
                    self.append_result(self.text_results, f"  • {key}: {count} occurrence(s)")
            
            self.append_result(self.text_results, "\nMatches:")
            for i, result in enumerate(results[:100], 1):  # Show first 100
                file_path = result.get('file', 'unknown')
                key = result.get('key', '')
                value = result.get('value', '')
                self.append_result(
                    self.text_results,
                    f"{i}. {os.path.basename(file_path)}: {key} = {value}"
                )
            
            if len(results) > 100:
                self.append_result(self.text_results, f"\n... and {len(results) - 100} more matches")
        
        self.btn_search.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.btn_save_results.setEnabled(bool(results))  # Enable if we have results
    
    def _on_failed(self, error):
        """Handle search failure."""
        self.append_result(self.text_results, f"\n❌ Error: {error}")
        self.btn_search.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
    
    def _save_results(self):
        """Save search results to file(s) with format options."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QButtonGroup, QDialogButtonBox, QLabel
        
        if not self.last_results:
            self.show_warning("No Results", "No search results to save. Please run a search first.")
            return
        
        # Create dialog for save options
        dialog = QDialog(self)
        dialog.setWindowTitle("Save Results Options")
        layout = QVBoxLayout(dialog)
        
        # Title
        layout.addWidget(QLabel("Choose how to save the results:"))
        
        # Radio buttons for save format
        self.radio_group = QButtonGroup(dialog)
        
        radio_single = QRadioButton("Single file (all results in one TXT)")
        radio_single.setToolTip("Save all results to a single text file")
        radio_single.setChecked(True)
        self.radio_group.addButton(radio_single, 0)
        layout.addWidget(radio_single)
        
        radio_per_file = QRadioButton("Per original file (one result file per source)")
        radio_per_file.setToolTip("Create one result file for each source file that had matches")
        self.radio_group.addButton(radio_per_file, 1)
        layout.addWidget(radio_per_file)
        
        radio_per_query = QRadioButton("Per query (group by search term)")
        radio_per_query.setToolTip("Group results by search query (key or value)")
        self.radio_group.addButton(radio_per_query, 2)
        layout.addWidget(radio_per_query)
        
        # OK/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        if dialog.exec() != QDialog.Accepted:
            return
        
        # Get selected option
        selected_option = self.radio_group.checkedId()
        
        # Execute save based on selection
        if selected_option == 0:
            self._save_single_file()
        elif selected_option == 1:
            self._save_per_original_file()
        elif selected_option == 2:
            self._save_per_query()
    
    def _save_single_file(self):
        """Save all results to a single text file."""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save All Results",
            "search_results.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("CLARIFY - JSON SEARCH RESULTS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total matches: {len(self.last_results)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, result in enumerate(self.last_results, 1):
                    file_path_res = result.get('file', 'unknown')
                    key = result.get('key', '')
                    value = result.get('value', '')
                    f.write(f"Match {i}:\n")
                    f.write(f"  File: {file_path_res}\n")
                    f.write(f"  Key: {key}\n")
                    f.write(f"  Value: {value}\n")
                    f.write("\n")
            
            self.show_info("Success", f"Results saved to:\n{file_path}")
        except Exception as e:
            self.show_error("Save Error", f"Failed to save results:\n{str(e)}")
    
    def _save_per_original_file(self):
        """Save results grouped by original source file."""
        from PySide6.QtWidgets import QFileDialog
        from collections import defaultdict
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Result Files"
        )
        
        if not output_dir:
            return
        
        try:
            # Group results by source file
            grouped = defaultdict(list)
            for result in self.last_results:
                source_file = result.get('file', 'unknown')
                grouped[source_file].append(result)
            
            # Save one file per source
            for source_file, results in grouped.items():
                base_name = os.path.basename(source_file)
                output_file = os.path.join(output_dir, f"{base_name}_results.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Results for: {source_file}\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Total matches: {len(results)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, result in enumerate(results, 1):
                        key = result.get('key', '')
                        value = result.get('value', '')
                        f.write(f"Match {i}:\n")
                        f.write(f"  Key: {key}\n")
                        f.write(f"  Value: {value}\n")
                        f.write("\n")
            
            self.show_info("Success", f"Saved {len(grouped)} result file(s) to:\n{output_dir}")
        except Exception as e:
            self.show_error("Save Error", f"Failed to save results:\n{str(e)}")
    
    def _save_per_query(self):
        """Save results grouped by search query (key or value)."""
        from PySide6.QtWidgets import QFileDialog
        from collections import defaultdict
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory for Query Result Files"
        )
        
        if not output_dir:
            return
        
        try:
            # Group by query (use key if present, else value)
            grouped = defaultdict(list)
            for result in self.last_results:
                query_key = result.get('key') or result.get('value') or 'unknown'
                # Use first part of key path for grouping
                group_name = query_key.split('.')[0] if '.' in query_key else query_key
                grouped[group_name].append(result)
            
            # Save one file per query group
            for query_name, results in grouped.items():
                # Sanitize filename
                safe_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in query_name)
                output_file = os.path.join(output_dir, f"query_{safe_name}_results.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Results for query: {query_name}\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Total matches: {len(results)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, result in enumerate(results, 1):
                        file_path = result.get('file', 'unknown')
                        key = result.get('key', '')
                        value = result.get('value', '')
                        f.write(f"Match {i}:\n")
                        f.write(f"  File: {file_path}\n")
                        f.write(f"  Key: {key}\n")
                        f.write(f"  Value: {value}\n")
                        f.write("\n")
            
            self.show_info("Success", f"Saved {len(grouped)} query result file(s) to:\n{output_dir}")
        except Exception as e:
            self.show_error("Save Error", f"Failed to save results:\n{str(e)}")
    
    def _clear(self):
        """Clear results."""
        self.clear_results(self.text_results)
        self.last_results = []
        self.btn_save_results.setEnabled(False)
    
    def _execute_action(self):
        """Execute the main action when ENTER is pressed."""
        self._search()
