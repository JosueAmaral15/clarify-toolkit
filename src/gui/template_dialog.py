#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Project Templates Dialog - Sprint v2.9.63"""

from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
from src.i18n.translator import tr

from ..template_manager import get_template_manager, ProjectTemplate


class TemplateDialog(QDialog):
    """Dialog for selecting and creating projects from templates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("template_dialog.title"))
        self.resize(700, 500)
        self.manager = get_template_manager()
        self.selected_template = None
        self._setup_ui()
        self._load_templates()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left: Template list
        left = QVBoxLayout()
        left.addWidget(QLabel(tr("template_dialog.lbl_available")))
        
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        left.addWidget(self.template_list)
        
        layout.addLayout(left, 1)
        
        # Right: Details + actions
        right = QVBoxLayout()
        right.addWidget(QLabel(tr("template_dialog.lbl_details")))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right.addWidget(self.details_text)
        
        right.addWidget(QLabel(tr("template_dialog.lbl_target_dir")))
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(str(Path.home() / "new_project"))
        dir_layout.addWidget(self.dir_edit)
        browse_btn = QPushButton(tr("template_dialog.btn_browse"))
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_btn)
        right.addLayout(dir_layout)
        
        create_btn = QPushButton(tr("template_dialog.btn_create"))
        create_btn.clicked.connect(self._create_project)
        right.addWidget(create_btn)
        
        close_btn = QPushButton(tr("template_dialog.btn_close"))
        close_btn.clicked.connect(self.close)
        right.addWidget(close_btn)
        
        layout.addLayout(right, 1)
    
    def _load_templates(self):
        for template in self.manager.list_templates():
            item = QListWidgetItem(f"{template.icon} {template.name}")
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)
    
    def _on_template_selected(self, current, previous):
        if not current:
            return
        
        template: ProjectTemplate = current.data(Qt.UserRole)
        self.selected_template = template
        
        details = f"<h3>{template.icon} {template.name}</h3>"
        details += f"<p><b>Description:</b> {template.description}</p>"
        details += f"<p><b>Category:</b> {template.category}</p>"
        details += f"<p><b>Files:</b> {len(template.files)}</p>"
        
        self.details_text.setHtml(details)
    
    def _browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if dir_path:
            self.dir_edit.setText(dir_path)
    
    def _create_project(self):
        if not self.selected_template:
            QMessageBox.warning(self, tr("template_dialog.msg_no_template_title"), tr("template_dialog.msg_no_template"))
            return
        
        target_dir = Path(self.dir_edit.text())
        
        if target_dir.exists() and any(target_dir.iterdir()):
            reply = QMessageBox.question(
                self, "Directory Not Empty",
                f"Directory already exists and is not empty.\nOverwrite files?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        try:
            self.manager.create_from_template(
                self.selected_template.id,
                target_dir,
                overwrite=True
            )
            
            QMessageBox.information(
                self, "Success",
                f"Project created successfully at:\n{target_dir}"
            )
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, tr("template.create_error_title"), tr("template.create_error").format(error=str(e)))
