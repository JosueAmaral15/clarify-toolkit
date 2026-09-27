#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Venn Diagram Dialog for Clarify
Interactive Venn diagram visualization for Set Operations results.

Features:
- 2-circle Venn diagram with QGraphicsView
- Click regions to view keys+values
- Color-coded regions (green/red/yellow)
- Statistics summary
- Export SVG

Author: Josué Amaral
Date: 2025-12-23
Version: v2.9.107
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=invalid-name  # Qt method name convention
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern

import json

from typing import Any, Dict

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QGraphicsEllipseItem, QGraphicsScene,
    QGraphicsTextItem, QGraphicsView, QGroupBox, QHBoxLayout,
    QLabel, QListWidget, QMessageBox, QPushButton, QSplitter,
    QTextEdit, QVBoxLayout
)

from src.i18n.translator import tr, tooltip_tr
from ..venn_diagram_generator import VennDiagramGenerator
from ..diff_analyzer import DiffAnalyzer


class InteractiveCircle(QGraphicsEllipseItem):
    """Interactive circle for Venn diagram regions."""

    def __init__(self, rect: QRectF, region: str, venn_data: Dict[str, Any], parent_dialog):
        super().__init__(rect)
        self.region = region
        self.venn_data = venn_data
        self.parent_dialog = parent_dialog

        # Set appearance
        region_data = venn_data["regions"][region]
        color = QColor(region_data["color"])
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))

        # Make clickable
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle click on region."""
        self.parent_dialog.show_region_details(self.region)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        """Highlight on hover."""
        self.setPen(QPen(Qt.blue, 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Remove highlight."""
        self.setPen(QPen(Qt.black, 2))
        super().hoverLeaveEvent(event)


class VennDiagramDialog(QDialog):
    """
    Dialog for interactive Venn diagram visualization.

    Features:
    - 2-circle Venn diagram (File A vs File B)
    - Click regions to view keys+values
    - Color-coded (green A, red B, yellow intersection)
    - Export SVG
    """

    def __init__(
        self,
        data_a: Any,
        data_b: Any,
        file_a_name: str,
        file_b_name: str,
        comparison_mode: str = "key_value",
        parent=None,
    ):
        """
        Initialize Venn diagram dialog.

        Args:
            data_a: First dataset
            data_b: Second dataset
            file_a_name: Name of File A
            file_b_name: Name of File B
            comparison_mode: Comparison mode (key_value, full_path_value, key_only)
            parent: Parent widget
        """
        super().__init__(parent)
        self.data_a = data_a
        self.data_b = data_b
        self.file_a_name = file_a_name
        self.file_b_name = file_b_name
        self.comparison_mode = comparison_mode

        # Analyze differences using DiffAnalyzer
        self.diff_result = DiffAnalyzer.analyze(data_a, data_b, comparison_mode)

        # Generate Venn diagram data
        self.venn_data = VennDiagramGenerator.generate(self.diff_result, file_a_name, file_b_name, comparison_mode)

        self.setWindowTitle(tr("venn_diagram.window_title").format(file_a_name=file_a_name, file_b_name=file_b_name))
        self.setModal(False)
        self.resize(1000, 600)
        self._init_ui()
        self._draw_venn_diagram()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"<h2>Venn Diagram: {self.file_a_name} vs {self.file_b_name}</h2>")
        layout.addWidget(title)

        # Summary
        summary_text = self.venn_data["summary"]
        summary_label = QLabel(summary_text)
        summary_label.setFont(QFont("Courier", 10))
        summary_label.setStyleSheet("color: #6A9955; font-weight: bold; padding: 5px;")
        layout.addWidget(summary_label)

        # Main splitter (Venn diagram | Details)
        splitter = QSplitter(Qt.Horizontal)

        # === Left: Venn Diagram ===
        venn_group = QGroupBox(tr("venn_diagram.group_venn"))
        venn_layout = QVBoxLayout(venn_group)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMinimumSize(500, 400)
        venn_layout.addWidget(self.view)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel(tr("venn_diagram.lbl_legend")))

        only_a_data = self.venn_data["regions"]["only_a"]
        legend_a = QLabel(f" {only_a_data['label']}: {only_a_data['description']} ")
        legend_a.setStyleSheet(f"background-color: {only_a_data['color']}; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_a)

        intersection_data = self.venn_data["regions"]["intersection"]
        legend_int = QLabel(f" {intersection_data['label']}: {intersection_data['description']} ")
        legend_int.setStyleSheet(
            f"background-color: {intersection_data['color']}; padding: 3px; border: 1px solid #aaa;"
        )
        legend_layout.addWidget(legend_int)

        only_b_data = self.venn_data["regions"]["only_b"]
        legend_b = QLabel(f" {only_b_data['label']}: {only_b_data['description']} ")
        legend_b.setStyleSheet(f"background-color: {only_b_data['color']}; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_b)

        legend_layout.addStretch()
        venn_layout.addLayout(legend_layout)

        splitter.addWidget(venn_group)

        # === Right: Details Panel ===
        details_group = QGroupBox(tr("venn_diagram.group_details"))
        details_layout = QVBoxLayout(details_group)

        self.lbl_region_title = QLabel(tr("venn_diagram.lbl_region_instruction"))
        self.lbl_region_title.setFont(QFont("", 11, QFont.Bold))
        details_layout.addWidget(self.lbl_region_title)

        # Keys list
        self.list_keys = QListWidget()
        self.list_keys.setFont(QFont("Courier", 9))
        self.list_keys.currentTextChanged.connect(self._on_key_selected)
        details_layout.addWidget(self.list_keys)

        # Value preview
        value_label = QLabel(tr("venn_diagram.lbl_value_preview"))
        details_layout.addWidget(value_label)

        self.text_value = QTextEdit()
        self.text_value.setReadOnly(True)
        self.text_value.setFont(QFont("Courier", 9))
        self.text_value.setMaximumHeight(150)
        details_layout.addWidget(self.text_value)

        splitter.addWidget(details_group)

        # Set splitter sizes (60% diagram, 40% details)
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)

        # === Buttons ===
        btn_layout = QHBoxLayout()

        btn_export_svg = QPushButton(f"💾 {tr('venn_diagram.btn_export_svg')}")
        btn_export_svg.setToolTip(tooltip_tr("venn.tooltip_export_svg"))
        btn_export_svg.clicked.connect(self._export_svg)
        btn_layout.addWidget(btn_export_svg)

        btn_layout.addStretch()

        btn_close = QPushButton(tr("venn_diagram.btn_close"))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _draw_venn_diagram(self):
        """Draw Venn diagram with 2 circles on QGraphicsScene."""
        # Diagram parameters
        scene_width = 480
        scene_height = 350
        radius = 100
        overlap = 40  # Overlap between circles for intersection

        # Circle centers
        center_a_x = scene_width / 2 - overlap
        center_a_y = scene_height / 2
        center_b_x = scene_width / 2 + overlap
        center_b_y = scene_height / 2

        # Create scene rect
        self.scene.setSceneRect(0, 0, scene_width, scene_height)

        # === Draw Circle A (Only A region) ===
        circle_a_rect = QRectF(center_a_x - radius, center_a_y - radius, radius * 2, radius * 2)
        circle_a = InteractiveCircle(circle_a_rect, "only_a", self.venn_data, self)
        circle_a.setOpacity(0.6)
        self.scene.addItem(circle_a)

        # === Draw Circle B (Only B region) ===
        circle_b_rect = QRectF(center_b_x - radius, center_b_y - radius, radius * 2, radius * 2)
        circle_b = InteractiveCircle(circle_b_rect, "only_b", self.venn_data, self)
        circle_b.setOpacity(0.6)
        self.scene.addItem(circle_b)

        # === Intersection region (overlap area) ===
        # Create a small circle at intersection for clicking
        intersection_radius = 50
        intersection_rect = QRectF(
            scene_width / 2 - intersection_radius / 2,
            scene_height / 2 - intersection_radius / 2,
            intersection_radius,
            intersection_radius,
        )
        intersection_circle = InteractiveCircle(intersection_rect, "intersection", self.venn_data, self)
        intersection_circle.setOpacity(0.8)
        self.scene.addItem(intersection_circle)

        # === Add labels ===
        # File A label
        label_a = QGraphicsTextItem(self.file_a_name)
        label_a.setFont(QFont("", 12, QFont.Bold))
        label_a.setPos(center_a_x - radius - 30, center_a_y - radius - 30)
        self.scene.addItem(label_a)

        # File B label
        label_b = QGraphicsTextItem(self.file_b_name)
        label_b.setFont(QFont("", 12, QFont.Bold))
        label_b.setPos(center_b_x + radius - 20, center_b_y - radius - 30)
        self.scene.addItem(label_b)

        # === Add counts in regions ===
        only_a_data = self.venn_data["regions"]["only_a"]
        count_a = QGraphicsTextItem(str(only_a_data["count"]))
        count_a.setFont(QFont("", 20, QFont.Bold))
        count_a.setPos(center_a_x - radius + 30, center_a_y - 15)
        self.scene.addItem(count_a)

        only_b_data = self.venn_data["regions"]["only_b"]
        count_b = QGraphicsTextItem(str(only_b_data["count"]))
        count_b.setFont(QFont("", 20, QFont.Bold))
        count_b.setPos(center_b_x + radius - 60, center_b_y - 15)
        self.scene.addItem(count_b)

        intersection_data = self.venn_data["regions"]["intersection"]
        count_int = QGraphicsTextItem(str(intersection_data["count"]))
        count_int.setFont(QFont("", 20, QFont.Bold))
        count_int.setPos(scene_width / 2 - 15, center_a_y - 15)
        self.scene.addItem(count_int)

        # Add instruction text
        instruction = QGraphicsTextItem("Click any region to view details →")
        instruction_font = QFont("", 10)
        instruction_font.setItalic(True)
        instruction.setFont(instruction_font)
        instruction.setDefaultTextColor(QColor("#666666"))
        instruction.setPos(scene_width / 2 - 120, scene_height - 40)
        self.scene.addItem(instruction)

    def show_region_details(self, region: str):
        """
        Show details for clicked region.

        Args:
            region: Region name ('only_a', 'only_b', 'intersection')
        """
        # Update title
        region_data = self.venn_data["regions"][region]
        self.lbl_region_title.setText(f"<b>{region_data['label']}</b> - {region_data['description']}")

        # Get key-value details
        details = VennDiagramGenerator.get_region_details(self.venn_data, region, self.diff_result)

        # Populate keys list
        self.list_keys.clear()
        self.current_details = {}  # Store for value preview

        for key, value in details:
            self.list_keys.addItem(key)
            self.current_details[key] = value

        # Clear value preview
        self.text_value.clear()

        # Show count
        if not details:
            self.text_value.setPlainText("(No keys in this region)")

    def _on_key_selected(self, key: str):
        """Show value preview when key is selected."""
        if not key or key not in self.current_details:
            return

        value = self.current_details[key]

        # Format value as JSON
        try:
            if isinstance(value, (dict, list)):
                formatted_value = json.dumps(value, indent=2, ensure_ascii=False)
            else:
                formatted_value = str(value)
        except Exception as e:
            formatted_value = f"Error formatting value: {e}"

        self.text_value.setPlainText(formatted_value)

    def _export_svg(self):
        """Export Venn diagram as SVG file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Venn Diagram as SVG",
            f"venn_{self.file_a_name}_vs_{self.file_b_name}.svg",
            "SVG Files (*.svg)",
        )

        if not file_path:
            return

        try:
            VennDiagramGenerator.export_svg(self.venn_data, file_path)

            QMessageBox.information(
                self,
                tr("venn_diagram.msg_export_success_title"),
                tr("venn_diagram.msg_export_success").format(path=file_path),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr("venn_diagram.msg_export_failed_title"),
                tr("venn_diagram.msg_export_failed").format(error=str(e)),
            )
