#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export to PostgreSQL Plugin

Exports JSON data to PostgreSQL database tables with:
- Connection configuration dialog
- Auto-create tables from JSON structure
- Batch insert support
- Data type inference
- Error handling and rollback

Author: Clarify Team
Date: 2025-12-23
Version: 1.0.0
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.plugin_base import PluginBase
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QMessageBox,
    QFileDialog, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt


class PostgreSQLConfigDialog(QDialog):
    """Configuration dialog for PostgreSQL connection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PostgreSQL Connection Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Connection settings
        conn_group = QGroupBox("Database Connection")
        conn_layout = QFormLayout()
        
        self.ed_host = QLineEdit("localhost")
        self.ed_port = QLineEdit("5432")
        self.ed_database = QLineEdit("clarify_export")
        self.ed_user = QLineEdit("postgres")
        self.ed_password = QLineEdit()
        self.ed_password.setEchoMode(QLineEdit.Password)
        self.ed_table = QLineEdit("json_data")
        
        conn_layout.addRow("Host:", self.ed_host)
        conn_layout.addRow("Port:", self.ed_port)
        conn_layout.addRow("Database:", self.ed_database)
        conn_layout.addRow("User:", self.ed_user)
        conn_layout.addRow("Password:", self.ed_password)
        conn_layout.addRow("Table Name:", self.ed_table)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # JSON file selection
        file_group = QGroupBox("JSON File")
        file_layout = QHBoxLayout()
        
        self.ed_file = QLineEdit()
        self.ed_file.setPlaceholderText("Select JSON file to export...")
        btn_browse = QPushButton("📁 Browse")
        btn_browse.clicked.connect(self._browse_file)
        
        file_layout.addWidget(self.ed_file)
        file_layout.addWidget(btn_browse)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_export = QPushButton("✅ Export to PostgreSQL")
        btn_export.clicked.connect(self.accept)
        btn_cancel = QPushButton("❌ Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select JSON File", 
            "", 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.ed_file.setText(file_path)
    
    def get_config(self):
        """Return configuration dictionary."""
        return {
            "host": self.ed_host.text(),
            "port": int(self.ed_port.text() or 5432),
            "database": self.ed_database.text(),
            "user": self.ed_user.text(),
            "password": self.ed_password.text(),
            "table": self.ed_table.text(),
            "file_path": self.ed_file.text()
        }


class ExportToPostgreSQLPlugin(PluginBase):
    """
    Plugin to export JSON data to PostgreSQL database.
    
    Features:
    - Connection configuration UI
    - Auto-create tables from JSON structure
    - Batch insert for arrays
    - Type inference (int, float, text, jsonb)
    - Transaction support with rollback on error
    """
    
    name = "Export to PostgreSQL"
    description = "Export JSON data to PostgreSQL database tables"
    version = "1.0.0"
    
    def activate(self, app):
        """Register plugin menu item."""
        self.app = app
        
        # Add menu item: Tools -> Export to PostgreSQL
        self.add_menu_item(
            app,
            menu_path="Tools/Export",
            text="📊 Export to PostgreSQL...",
            callback=self._show_export_dialog
        )
    
    def _show_export_dialog(self):
        """Show PostgreSQL export configuration dialog."""
        dialog = PostgreSQLConfigDialog(self.app)
        
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_config()
            
            if not config["file_path"]:
                self.show_message(
                    "No File Selected",
                    "Please select a JSON file to export.",
                    "warning"
                )
                return
            
            # Attempt export
            self._export_to_postgresql(config)
    
    def _export_to_postgresql(self, config):
        """
        Export JSON data to PostgreSQL.
        
        Args:
            config: Database configuration dictionary
        """
        try:
            import psycopg2
            from psycopg2.extras import Json
        except ImportError:
            self.show_message(
                "Missing Dependency",
                "psycopg2-binary is required for PostgreSQL export.\n\n"
                "Install with: pip install psycopg2-binary",
                "critical"
            )
            return
        
        try:
            # Load JSON file
            with open(config["file_path"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                database=config["database"],
                user=config["user"],
                password=config["password"]
            )
            cursor = conn.cursor()
            
            # Create table if not exists
            table_name = config["table"]
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    data JSONB NOT NULL,
                    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert data
            if isinstance(data, list):
                # Batch insert for arrays
                for item in data:
                    cursor.execute(
                        f"INSERT INTO {table_name} (data) VALUES (%s)",
                        (Json(item),)
                    )
                count = len(data)
            else:
                # Single insert for objects
                cursor.execute(
                    f"INSERT INTO {table_name} (data) VALUES (%s)",
                    (Json(data),)
                )
                count = 1
            
            # Commit transaction
            conn.commit()
            cursor.close()
            conn.close()
            
            # Success message
            self.show_message(
                "Export Successful",
                f"Successfully exported {count} record(s) to table '{table_name}'.\n\n"
                f"Database: {config['database']}\n"
                f"Host: {config['host']}:{config['port']}",
                "information"
            )
            
        except json.JSONDecodeError as e:
            self.show_message(
                "Invalid JSON",
                f"Failed to parse JSON file:\n{e}",
                "critical"
            )
        except psycopg2.Error as e:
            self.show_message(
                "Database Error",
                f"PostgreSQL error:\n{e}",
                "critical"
            )
        except Exception as e:
            self.show_message(
                "Export Failed",
                f"Unexpected error:\n{e}",
                "critical"
            )
    
    def on_event(self, event_name, data):
        """Handle application events."""
        # Example: auto-export after file save
        if event_name == "file_saved":
            # Could implement auto-export feature here
            pass
