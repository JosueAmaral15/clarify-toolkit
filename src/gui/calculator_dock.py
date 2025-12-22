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
    QGroupBox, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ..calculator_memory import CalculatorMemory
from ..statistics_manager import StatisticsManager


class CompareDialog(QDialog):
    """Dialog to compare statistics between two memory slots."""
    
    def __init__(self, comparison_data: dict, parent=None):
        super().__init__(parent)
        self.comparison_data = comparison_data
        self.setWindowTitle("Compare Memory Slots")
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
        btn_close = QPushButton("Close")
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory = CalculatorMemory()
        self._init_ui()
        self._refresh_table()
    
    def _init_ui(self):
        """Initialize Calculator dock UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Calculator Memory Slots")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info label
        info = QLabel("Store JSON result sets in memory slots with statistics tracking")
        info.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info)
        
        # Statistics table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setRowCount(5)  # 5 slots (A-E)
        self.table.setHorizontalHeaderLabels([
            "Slot", "Source", "Count", "Size", "Depth", "Unique Keys", "Dup Keys", "Types"
        ])
        
        # Configure table appearance
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        # Actions group
        actions_group = QGroupBox("Slot Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        # Slot selector
        self.combo_slot = QComboBox()
        self.combo_slot.addItems(CalculatorMemory.SLOT_NAMES)
        actions_layout.addWidget(QLabel("Select Slot:"))
        actions_layout.addWidget(self.combo_slot)
        
        # Buttons
        self.btn_recall = QPushButton("📤 Recall")
        self.btn_recall.setToolTip("Load data from selected slot")
        self.btn_recall.clicked.connect(self._recall_slot)
        actions_layout.addWidget(self.btn_recall)
        
        self.btn_view = QPushButton("👁️ View Details")
        self.btn_view.setToolTip("View detailed statistics for slot")
        self.btn_view.clicked.connect(self._view_details)
        actions_layout.addWidget(self.btn_view)
        
        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.setToolTip("Clear selected slot")
        self.btn_clear.clicked.connect(self._clear_slot)
        actions_layout.addWidget(self.btn_clear)
        
        layout.addWidget(actions_group)
        
        # Comparison group
        compare_group = QGroupBox("Compare Slots")
        compare_layout = QHBoxLayout(compare_group)
        
        self.combo_compare1 = QComboBox()
        self.combo_compare1.addItems(CalculatorMemory.SLOT_NAMES)
        compare_layout.addWidget(QLabel("Slot 1:"))
        compare_layout.addWidget(self.combo_compare1)
        
        compare_layout.addWidget(QLabel("vs"))
        
        self.combo_compare2 = QComboBox()
        self.combo_compare2.addItems(CalculatorMemory.SLOT_NAMES)
        self.combo_compare2.setCurrentIndex(1)  # Default to B
        compare_layout.addWidget(QLabel("Slot 2:"))
        compare_layout.addWidget(self.combo_compare2)
        
        self.btn_compare = QPushButton("⚖️ Compare")
        self.btn_compare.setToolTip("Compare statistics between two slots")
        self.btn_compare.clicked.connect(self._compare_slots)
        compare_layout.addWidget(self.btn_compare)
        
        layout.addWidget(compare_group)
        
        # Clear all button
        self.btn_clear_all = QPushButton("🗑️ Clear All Slots")
        self.btn_clear_all.setToolTip("Clear all memory slots")
        self.btn_clear_all.clicked.connect(self._clear_all_slots)
        self.btn_clear_all.setStyleSheet("background-color: #dc3545; color: white;")
        layout.addWidget(self.btn_clear_all)
    
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
                "Stored",
                f"Result stored in slot {slot_name}\nSource: {source}"
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to store result in slot {slot_name}"
            )
        
        return success
    
    def _recall_slot(self):
        """Recall data from selected slot."""
        slot_name = self.combo_slot.currentText()
        
        if self.memory.is_slot_empty(slot_name):
            QMessageBox.information(self, "Empty Slot", f"Slot {slot_name} is empty")
            return
        
        data = self.memory.recall_result(slot_name)
        slot_info = self.memory.get_slot_info(slot_name)
        
        # Emit signal for integration with other docks
        self.data_recalled.emit(data)
        
        QMessageBox.information(
            self,
            "Recalled",
            f"Data from slot {slot_name} recalled\n"
            f"Source: {slot_info['source']}\n"
            f"Timestamp: {slot_info['timestamp']}"
        )
    
    def _view_details(self):
        """View detailed statistics for selected slot."""
        slot_name = self.combo_slot.currentText()
        
        if self.memory.is_slot_empty(slot_name):
            QMessageBox.information(self, "Empty Slot", f"Slot {slot_name} is empty")
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
            QMessageBox.information(self, "Empty Slot", f"Slot {slot_name} is already empty")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            f"Clear slot {slot_name}?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.memory.clear_slot(slot_name)
            self._refresh_table()
            QMessageBox.information(self, "Cleared", f"Slot {slot_name} cleared")
    
    def _clear_all_slots(self):
        """Clear all memory slots."""
        occupied = self.memory.get_occupied_slots()
        
        if not occupied:
            QMessageBox.information(self, "No Data", "All slots are already empty")
            return
        
        reply = QMessageBox.warning(
            self,
            "Confirm Clear All",
            f"Clear all {len(occupied)} occupied slots?\n"
            f"Slots: {', '.join(occupied)}\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.memory.clear_all_slots()
            self._refresh_table()
            QMessageBox.information(self, "Cleared", "All slots cleared")
    
    def _compare_slots(self):
        """Compare statistics between two slots."""
        slot1 = self.combo_compare1.currentText()
        slot2 = self.combo_compare2.currentText()
        
        if slot1 == slot2:
            QMessageBox.warning(self, "Invalid Selection", "Please select two different slots")
            return
        
        if self.memory.is_slot_empty(slot1) or self.memory.is_slot_empty(slot2):
            QMessageBox.warning(
                self,
                "Empty Slot",
                f"Both slots must have data\n"
                f"Slot {slot1}: {'Empty' if self.memory.is_slot_empty(slot1) else 'OK'}\n"
                f"Slot {slot2}: {'Empty' if self.memory.is_slot_empty(slot2) else 'OK'}"
            )
            return
        
        comparison = self.memory.compare_slots(slot1, slot2)
        
        if comparison:
            dialog = CompareDialog(comparison, self)
            dialog.exec()
