"""
Calculator Dock for Clarify
Memory-based calculator with statistics for JSON result sets.

Author: Josué Amaral
Date: 2025/12/22
Version: 2.9.98
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QComboBox, QDialog, QTextEdit,
    QGroupBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..calculator_memory import CalculatorMemory
from ..statistics_manager import StatisticsManager
from ..calculator_operations import CalculatorOperations
from ..accessibility_manager import AccessibilityManager
from .recall_dialog import RecallDialog
from .operation_preview_dialog import OperationPreviewDialog
from ..i18n.translator import tr


class CompareDialog(QDialog):
    """Dialog to compare statistics between two memory slots."""
    
    def __init__(self, comparison_data: dict, parent=None):
        super().__init__(parent)
        self.comparison_data = comparison_data
        self.setWindowTitle(tr("calculator.dialog_compare_title"))
        self.setModal(True)
        self.resize(700, 500)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize compare dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        slot1 = self.comparison_data['slot1']
        slot2 = self.comparison_data['slot2']
        title = QLabel(f"Comparison: Slot {slot1} vs Slot {slot2}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Comparison text
        txt_compare = QTextEdit()
        txt_compare.setReadOnly(True)
        txt_compare.setFont(QFont("Courier", 10))
        
        # Format comparison
        stats1 = self.comparison_data['slot1_stats']
        stats2 = self.comparison_data['slot2_stats']
        diffs = self.comparison_data['differences']
        
        comparison_text = StatisticsManager.format_comparative_statistics(
            stats1, stats2, {}, 
            f"Slot {slot1}", f"Slot {slot2}", "Difference"
        )
        
        # Add difference summary
        comparison_text += "\n\n" + "="*70 + "\n"
        comparison_text += "DIFFERENCE SUMMARY:\n"
        comparison_text += "="*70 + "\n"
        comparison_text += f"Total Keys:   {diffs['total_keys_diff']:+d}\n"
        comparison_text += f"Unique Keys:  {diffs['unique_keys_diff']:+d}\n"
        comparison_text += f"Size:         {diffs['size_diff']:+d} bytes\n"
        comparison_text += f"Max Depth:    {diffs['depth_diff']:+d} levels\n"
        
        txt_compare.setText(comparison_text)
        layout.addWidget(txt_compare)
        
        # Close button
        btn_close = QPushButton(tr("calculator.btn_close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class CalculatorDock(QWidget):
    """
    Calculator dock with memory slots for JSON result sets.
    
    Features:
    - 5 memory slots (A, B, C, D, E) for storing results
    - Statistics display (count, size, depth, types, keys)
    - Store, Recall, Clear operations per slot
    - Compare statistics between slots
    - QSettings persistence across sessions
    """
    
    # Signal emitted when recalling data from slot (for integration)
    data_recalled = Signal(object)  # Emits JSON data
    
    # Signal emitted when sending data to Set Operations (for integration)
    send_to_set_operations = Signal(dict, str)  # (data, source_description)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory = CalculatorMemory()
        self.operations = CalculatorOperations()
        self._init_ui()
        self._refresh_table()
    
    def _init_ui(self):
        """Initialize Calculator dock UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel(tr("calculator.title"))
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info label
        info = QLabel(tr("calculator.info"))
        info.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info)
        
        # Statistics table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setRowCount(5)  # 5 slots (A-E)
        self.table.setHorizontalHeaderLabels([
            tr("calculator.header_slot"), tr("calculator.header_source"), 
            tr("calculator.header_count"), tr("calculator.header_size"), 
            tr("calculator.header_depth"), tr("calculator.header_unique_keys"), 
            tr("calculator.header_dup_keys"), tr("calculator.header_types")
        ])
        
        # Configure table appearance
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Actions group
        actions_group = QGroupBox("Slot Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Slot selector
        self.combo_slot = QComboBox()
        self.combo_slot.addItems(CalculatorMemory.SLOT_NAMES)
        actions_layout.addWidget(QLabel(tr("calculator.lbl_select_slot")))
        actions_layout.addWidget(self.combo_slot)
        
        # Buttons
        self.btn_recall = QPushButton(tr("calculator.btn_recall"))
        self.btn_recall.setToolTip("Load data from selected slot")
        self.btn_recall.clicked.connect(self._recall_slot)
        actions_layout.addWidget(self.btn_recall)
        
        self.btn_view = QPushButton(tr("calculator.btn_view"))
        self.btn_view.setToolTip("View detailed statistics for slot")
        self.btn_view.clicked.connect(self._view_details)
        actions_layout.addWidget(self.btn_view)
        
        self.btn_clear = QPushButton(tr("calculator.btn_clear"))
        self.btn_clear.setToolTip("Clear selected slot")
        self.btn_clear.clicked.connect(self._clear_slot)
        actions_layout.addWidget(self.btn_clear)
        
        layout.addWidget(actions_group)
        
        # Comparison group
        compare_group = QGroupBox(tr("calculator.group_compare"))
        compare_layout = QHBoxLayout(compare_group)
        
        self.combo_compare1 = QComboBox()
        self.combo_compare1.addItems(CalculatorMemory.SLOT_NAMES)
        compare_layout.addWidget(QLabel(tr("calculator.lbl_slot1")))
        compare_layout.addWidget(self.combo_compare1)
        
        compare_layout.addWidget(QLabel(tr("calculator.dialog_compare_vs")))
        
        self.combo_compare2 = QComboBox()
        self.combo_compare2.addItems(CalculatorMemory.SLOT_NAMES)
        self.combo_compare2.setCurrentIndex(1)  # Default to B
        compare_layout.addWidget(QLabel(tr("calculator.lbl_slot2")))
        compare_layout.addWidget(self.combo_compare2)
        
        self.btn_compare = QPushButton(tr("calculator.btn_compare"))
        self.btn_compare.setToolTip("Compare statistics between two slots")
        self.btn_compare.clicked.connect(self._compare_slots)
        compare_layout.addWidget(self.btn_compare)
        
        layout.addWidget(compare_group)
        
        # Operations group (v2.9.101)
        operations_group = QGroupBox(tr("calculator.group_operations"))
        operations_layout = QVBoxLayout(operations_group)
        
        # Slot selectors row
        selectors_layout = QHBoxLayout()
        
        selectors_layout.addWidget(QLabel(tr("calculator.lbl_slot1")))
        self.combo_op_slot1 = QComboBox()
        self.combo_op_slot1.addItems(CalculatorMemory.SLOT_NAMES)
        selectors_layout.addWidget(self.combo_op_slot1)
        
        selectors_layout.addWidget(QLabel(tr("calculator.lbl_slot2")))
        self.combo_op_slot2 = QComboBox()
        self.combo_op_slot2.addItems(CalculatorMemory.SLOT_NAMES)
        self.combo_op_slot2.setCurrentIndex(1)  # Default to B
        selectors_layout.addWidget(self.combo_op_slot2)
        
        operations_layout.addLayout(selectors_layout)
        
        # Operation buttons row
        op_buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton(tr("calculator.btn_add"))
        self.btn_add.setToolTip("Deep merge: Slot 1 + Slot 2 (v2.9.100 merge logic)")
        self.btn_add.clicked.connect(lambda: self._execute_operation('add'))
        op_buttons_layout.addWidget(self.btn_add)
        
        self.btn_intersection = QPushButton(tr("calculator.btn_intersection"))
        self.btn_intersection.setToolTip("Common keys: Slot 1 ∩ Slot 2")
        self.btn_intersection.clicked.connect(lambda: self._execute_operation('intersection'))
        op_buttons_layout.addWidget(self.btn_intersection)
        
        self.btn_union = QPushButton(tr("calculator.btn_union"))
        self.btn_union.setToolTip("All keys: Slot 1 ∪ Slot 2")
        self.btn_union.clicked.connect(lambda: self._execute_operation('union'))
        op_buttons_layout.addWidget(self.btn_union)
        
        self.btn_difference = QPushButton(tr("calculator.btn_difference"))
        self.btn_difference.setToolTip("Keys only in Slot 1: Slot 1 − Slot 2")
        self.btn_difference.clicked.connect(lambda: self._execute_operation('difference'))
        op_buttons_layout.addWidget(self.btn_difference)
        
        operations_layout.addLayout(op_buttons_layout)
        
        layout.addWidget(operations_group)
        
        # Clear all button
        self.btn_clear_all = QPushButton(tr("calculator.btn_clear_all"))
        self.btn_clear_all.setToolTip("Clear all memory slots")
        self.btn_clear_all.clicked.connect(self._clear_all_slots)
        self.btn_clear_all.setStyleSheet("background-color: #dc3545; color: white;")
        layout.addWidget(self.btn_clear_all)
        
        # Apply accessibility labels (v2.9.104)
        self._apply_accessibility()
    
    def _apply_accessibility(self):
        """Apply accessibility labels to all widgets (v2.9.104)."""
        # Memory table
        AccessibilityManager.set_accessible_widget(
            self.table, "Calculator - Table - Memory Slots", 
            "Table showing 5 memory slots with statistics (count, size, depth, keys, types)"
        )
        
        # Slot actions group
        AccessibilityManager.set_accessible_widget(
            self.combo_slot, "Calculator - Combo - Select Slot",
            "Select memory slot (A, B, C, D, or E) for action"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_recall, "Calculator - Button - Recall Slot",
            "Load and view data stored in selected memory slot"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_view, "Calculator - Button - View Details",
            "View detailed statistics for selected slot (count, size, depth, keys, types)"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_clear, "Calculator - Button - Clear Slot",
            "Clear selected memory slot (confirm before delete)"
        )
        
        # Comparison group
        AccessibilityManager.set_accessible_widget(
            self.combo_compare1, "Calculator - Combo - Compare Slot 1",
            "Select first memory slot for comparison"
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_compare2, "Calculator - Combo - Compare Slot 2",
            "Select second memory slot for comparison"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_compare, "Calculator - Button - Compare Slots",
            "Compare statistics between two memory slots (shows differences)"
        )
        
        # Operations group (v2.9.101)
        AccessibilityManager.set_accessible_widget(
            self.combo_op_slot1, "Calculator - Combo - Operation Slot 1",
            "Select first memory slot for operation (must contain data)"
        )
        AccessibilityManager.set_accessible_widget(
            self.combo_op_slot2, "Calculator - Combo - Operation Slot 2",
            "Select second memory slot for operation (must contain data)"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_add, "Calculator - Button - Add Operation",
            "Add (deep merge) two memory slots using JSON merge algorithm"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_intersection, "Calculator - Button - Intersection Operation",
            "Calculate intersection (common keys) between two slots"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_union, "Calculator - Button - Union Operation",
            "Calculate union (all keys) between two slots (slot 2 overwrites slot 1)"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_difference, "Calculator - Button - Difference Operation",
            "Calculate difference (keys only in slot 1, not in slot 2)"
        )
        
        # Clear all button
        AccessibilityManager.set_accessible_widget(
            self.btn_clear_all, "Calculator - Button - Clear All Slots",
            "Clear all 5 memory slots (confirm before delete all)"
        )
    
    def _refresh_table(self):
        """Refresh statistics table with current slot data."""
        summary = self.memory.get_all_slots_summary()
        
        for row, slot_data in enumerate(summary):
            # Slot name
            self.table.setItem(row, 0, QTableWidgetItem(slot_data['slot_name']))
            
            if slot_data['stats']:
                # Slot has data
                stats = slot_data['stats']
                
                # Source
                source = slot_data['source'] or "Unknown"
                self.table.setItem(row, 1, QTableWidgetItem(source))
                
                # Count (total keys)
                self.table.setItem(row, 2, QTableWidgetItem(str(stats['total_keys'])))
                
                # Size (formatted)
                size_str = StatisticsManager.format_size(stats['size_bytes'])
                self.table.setItem(row, 3, QTableWidgetItem(size_str))
                
                # Depth
                self.table.setItem(row, 4, QTableWidgetItem(str(stats['max_depth'])))
                
                # Unique keys
                self.table.setItem(row, 5, QTableWidgetItem(str(stats['unique_keys'])))
                
                # Duplicate keys
                dup_keys = stats['total_keys'] - stats['unique_keys']
                self.table.setItem(row, 6, QTableWidgetItem(str(dup_keys)))
                
                # Types (compact format)
                types = stats['value_types']
                types_str = f"S:{types.get('string', 0)} N:{types.get('number', 0)} B:{types.get('bool', 0)}"
                self.table.setItem(row, 7, QTableWidgetItem(types_str))
            else:
                # Empty slot
                self.table.setItem(row, 1, QTableWidgetItem("(Empty)"))
                for col in range(2, 8):
                    self.table.setItem(row, col, QTableWidgetItem("-"))
    
    def store_result(self, data: any, source: str = "Unknown") -> bool:
        """
        Store result in currently selected slot.
        
        Args:
            data: JSON data to store
            source: Source description
        
        Returns:
            True if stored successfully
        """
        slot_name = self.combo_slot.currentText()
        success = self.memory.store_result(slot_name, data, source)
        
        if success:
            self._refresh_table()
            QMessageBox.information(
                self,
                tr("calculator.msg_stored_title"),
                tr("calculator.msg_stored_success").format(slot_name, source)
            )
        else:
            QMessageBox.warning(
                self,
                tr("calculator.msg_store_error_title"),
                tr("calculator.msg_store_error_msg").format(slot_name)
            )
        
        return success
    
    def _recall_slot(self):
        """Recall data from selected slot (v2.9.101 enhanced with RecallDialog)."""
        slot_name = self.combo_slot.currentText()
        
        if self.memory.is_slot_empty(slot_name):
            QMessageBox.information(self, tr("calculator.msg_empty_slot_title"), tr("calculator.msg_empty_slot").format(slot_name))
            return
        
        slot_info = self.memory.get_slot_info(slot_name)
        
        # Open RecallDialog with Export/Copy/Send options
        dialog = RecallDialog(
            slot_name=slot_name,
            slot_data=slot_info['data'],
            slot_stats=slot_info['stats'],
            source=slot_info['source'],
            timestamp=slot_info['timestamp'],
            parent=self
        )
        
        # Connect send_to_set_operations signal
        dialog.send_to_set_operations.connect(self._handle_send_to_set_operations)
        
        dialog.exec()
        
        # Emit legacy signal for backward compatibility
        self.data_recalled.emit(slot_info['data'])
    
    def _view_details(self):
        """View detailed statistics for selected slot."""
        slot_name = self.combo_slot.currentText()
        
        if self.memory.is_slot_empty(slot_name):
            QMessageBox.information(self, tr("calculator.msg_empty_slot_title"), tr("calculator.msg_empty_slot").format(slot_name))
            return
        
        slot_info = self.memory.get_slot_info(slot_name)
        stats = slot_info['stats']
        
        # Format detailed stats
        details = f"SLOT {slot_name} - DETAILED STATISTICS\n"
        details += "="*50 + "\n\n"
        details += f"Source: {slot_info['source']}\n"
        details += f"Timestamp: {slot_info['timestamp']}\n\n"
        details += StatisticsManager.format_statistics_text(stats)
        
        # Show in message box
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Slot {slot_name} Details")
        msg.setText(details)
        msg.setFont(QFont("Courier", 9))
        msg.exec()
    
    def _clear_slot(self):
        """Clear selected slot."""
        slot_name = self.combo_slot.currentText()
        
        if self.memory.is_slot_empty(slot_name):
            QMessageBox.information(self, tr("calculator.msg_empty_slot_title"), tr("calculator.msg_empty_slot_already").format(slot_name))
            return
        
        reply = QMessageBox.question(
            self,
            tr("calculator.msg_confirm_clear_title"),
            tr("calculator.msg_confirm_clear").format(slot_name),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.memory.clear_slot(slot_name)
            self._refresh_table()
            QMessageBox.information(self, tr("calculator.msg_cleared_title"), tr("calculator.msg_cleared_slot").format(slot_name))
    
    def _clear_all_slots(self):
        """Clear all memory slots."""
        occupied = self.memory.get_occupied_slots()
        
        if not occupied:
            QMessageBox.information(self, tr("calculator.msg_no_data_title"), tr("calculator.msg_no_data"))
            return
        
        reply = QMessageBox.warning(
            self,
            tr("calculator.msg_confirm_clear_all_title"),
            tr("calculator.msg_confirm_clear_all").format(len(occupied), ', '.join(occupied)),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.memory.clear_all_slots()
            self._refresh_table()
            QMessageBox.information(self, tr("calculator.msg_cleared_title"), tr("calculator.msg_cleared_all"))
    
    def _compare_slots(self):
        """Compare statistics between two slots."""
        slot1 = self.combo_compare1.currentText()
        slot2 = self.combo_compare2.currentText()
        
        if slot1 == slot2:
            QMessageBox.warning(self, tr("calculator.msg_invalid_selection_title"), tr("calculator.msg_invalid_selection"))
            return
        
        if self.memory.is_slot_empty(slot1) or self.memory.is_slot_empty(slot2):
            status1 = tr("calculator.status_empty") if self.memory.is_slot_empty(slot1) else tr("calculator.status_ok")
            status2 = tr("calculator.status_empty") if self.memory.is_slot_empty(slot2) else tr("calculator.status_ok")
            QMessageBox.warning(
                self,
                tr("calculator.msg_empty_slot_title"),
                tr("calculator.msg_empty_slot_compare").format(slot1, status1, slot2, status2)
            )
            return
        
        comparison = self.memory.compare_slots(slot1, slot2)
        
        if comparison:
            dialog = CompareDialog(comparison, self)
            dialog.exec()
    
    def _execute_operation(self, operation: str):
        """Execute operation between two slots (v2.9.101)."""
        slot1 = self.combo_op_slot1.currentText()
        slot2 = self.combo_op_slot2.currentText()
        
        # Validate selection
        if slot1 == slot2:
            QMessageBox.warning(self, tr("calculator.msg_invalid_selection_title"), tr("calculator.msg_invalid_selection"))
            return
        
        # Get slot data
        data1 = self.memory.recall_result(slot1)
        data2 = self.memory.recall_result(slot2)
        
        # Validate data
        valid, error_msg = self.operations.validate_operation_data(data1, data2)
        if not valid:
            QMessageBox.warning(self, tr("calculator.msg_operation_failed_title"), error_msg)
            return
        
        # Execute operation
        if operation == 'add':
            success, result, message = self.operations.add(data1, data2)
        elif operation == 'intersection':
            success, result, message = self.operations.intersection(data1, data2, comparison_mode='key_value')
        elif operation == 'union':
            success, result, message = self.operations.union(data1, data2, comparison_mode='key_value')
        elif operation == 'difference':
            success, result, message = self.operations.difference(data1, data2, comparison_mode='key_value')
        else:
            QMessageBox.critical(self, "Error", f"Unknown operation: {operation}")
            return
        
        if not success:
            QMessageBox.critical(self, "Operation Failed", message)
            return
        
        # Calculate statistics for result
        result_stats = StatisticsManager.calculate_statistics(result)
        
        # Get available slots for storage
        available_slots = [s for s in CalculatorMemory.SLOT_NAMES if self.memory.is_slot_empty(s)]
        
        # Get operation description
        operation_desc = self.operations.get_operation_description(operation, slot1, slot2)
        
        # Show preview dialog
        preview_dialog = OperationPreviewDialog(
            operation_desc=operation_desc,
            result_data=result,
            result_stats=result_stats,
            message=message,
            available_slots=available_slots,
            parent=self
        )
        
        preview_dialog.exec()
        
        # Check if user wants to store result
        store, target_slot = preview_dialog.get_storage_info()
        
        if store and target_slot:
            # Store result in selected slot
            source = f"Operation: {operation_desc}"
            success = self.memory.store_result(target_slot, result, source)
            
            if success:
                self._refresh_table()
                QMessageBox.information(
                    self,
                    "Stored",
                    f"Operation result stored in Slot {target_slot}\n\n{message}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Storage Failed",
                    f"Failed to store result in Slot {target_slot}"
                )
    
    def _handle_send_to_set_operations(self, data: dict, slot_name: str):
        """Handle send to Set Operations signal from RecallDialog."""
        source_description = f"Calculator Memory Slot {slot_name}"
        self.send_to_set_operations.emit(data, source_description)
