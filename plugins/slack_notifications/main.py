#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Slack Notifications Plugin

Sends notifications to Slack channels when operations complete:
- Search completed
- Rewrite completed  
- AI processing finished
- Errors and warnings

Uses Slack Incoming Webhooks for simple integration.

Author: Clarify Team
Date: 2025-12-23
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.plugin_base import PluginBase
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QGroupBox,
    QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt


class SlackConfigDialog(QDialog):
    """Configuration dialog for Slack webhook."""
    
    def __init__(self, parent=None, current_webhook="", current_events=None):
        super().__init__(parent)
        self.setWindowTitle("Slack Notifications Settings")
        self.setMinimumWidth(600)
        
        if current_events is None:
            current_events = ["search_completed", "rewrite_completed", "ai_request_completed"]
        
        layout = QVBoxLayout()
        
        # Webhook URL
        webhook_group = QGroupBox("Slack Webhook Configuration")
        webhook_layout = QFormLayout()
        
        self.ed_webhook = QLineEdit(current_webhook)
        self.ed_webhook.setPlaceholderText("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
        
        lbl_help = QLabel(
            "Get webhook URL from: <a href='https://api.slack.com/messaging/webhooks'>"
            "https://api.slack.com/messaging/webhooks</a>"
        )
        lbl_help.setOpenExternalLinks(True)
        lbl_help.setWordWrap(True)
        
        webhook_layout.addRow("Webhook URL:", self.ed_webhook)
        webhook_layout.addRow("", lbl_help)
        
        webhook_group.setLayout(webhook_layout)
        layout.addWidget(webhook_group)
        
        # Event selection
        events_group = QGroupBox("Notify on Events")
        events_layout = QVBoxLayout()
        
        self.chk_search = QCheckBox("Search completed")
        self.chk_search.setChecked("search_completed" in current_events)
        
        self.chk_rewrite = QCheckBox("JSON rewrite completed")
        self.chk_rewrite.setChecked("rewrite_completed" in current_events)
        
        self.chk_ai = QCheckBox("AI processing completed")
        self.chk_ai.setChecked("ai_request_completed" in current_events)
        
        self.chk_file_saved = QCheckBox("File saved")
        self.chk_file_saved.setChecked("file_saved" in current_events)
        
        events_layout.addWidget(self.chk_search)
        events_layout.addWidget(self.chk_rewrite)
        events_layout.addWidget(self.chk_ai)
        events_layout.addWidget(self.chk_file_saved)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        # Test button
        btn_test = QPushButton("🧪 Send Test Notification")
        btn_test.clicked.connect(self._test_webhook)
        layout.addWidget(btn_test)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Save Settings")
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("❌ Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _test_webhook(self):
        """Test Slack webhook with a sample message."""
        webhook_url = self.ed_webhook.text().strip()
        if not webhook_url:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Webhook", "Please enter a webhook URL first.")
            return
        
        try:
            import requests
            
            payload = {
                "text": "🧪 Test notification from Clarify",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Test Notification*\n\nClarify Slack plugin is working! ✅"
                        }
                    }
                ]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "Test Successful", 
                    "Test notification sent to Slack successfully!"
                )
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "Test Failed", 
                    f"Slack returned status {response.status_code}:\n{response.text}"
                )
                
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to send test notification:\n{e}"
            )
    
    def get_config(self):
        """Return configuration dictionary."""
        events = []
        if self.chk_search.isChecked():
            events.append("search_completed")
        if self.chk_rewrite.isChecked():
            events.append("rewrite_completed")
        if self.chk_ai.isChecked():
            events.append("ai_request_completed")
        if self.chk_file_saved.isChecked():
            events.append("file_saved")
        
        return {
            "webhook_url": self.ed_webhook.text().strip(),
            "events": events
        }


class SlackNotificationsPlugin(PluginBase):
    """
    Plugin to send Slack notifications for Clarify operations.
    
    Features:
    - Configurable webhook URL
    - Selective event notifications
    - Rich message formatting with Slack blocks
    - Error handling
    """
    
    name = "Slack Notifications"
    description = "Send notifications to Slack when operations complete"
    version = "1.0.0"
    
    def activate(self, app):
        """Register plugin menu item and load settings."""
        self.app = app
        
        # Load saved settings
        self.webhook_url = self.get_setting("webhook_url", "")
        self.enabled_events = self.get_setting("events", 
            ["search_completed", "rewrite_completed", "ai_request_completed"])
        
        # Add menu item: Tools -> Slack Notifications Settings
        self.add_menu_item(
            app,
            menu_path="Tools/Integrations",
            text="💬 Slack Notifications Settings...",
            callback=self._show_settings_dialog
        )
    
    def _show_settings_dialog(self):
        """Show Slack configuration dialog."""
        dialog = SlackConfigDialog(
            self.app, 
            self.webhook_url, 
            self.enabled_events
        )
        
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_config()
            
            # Save settings
            self.webhook_url = config["webhook_url"]
            self.enabled_events = config["events"]
            
            self.set_setting("webhook_url", self.webhook_url)
            self.set_setting("events", self.enabled_events)
            
            self.show_message(
                "Settings Saved",
                "Slack notification settings have been saved successfully.",
                "information"
            )
    
    def on_event(self, event_name, data):
        """Handle application events and send Slack notifications."""
        # Check if event is enabled and webhook is configured
        if event_name not in self.enabled_events or not self.webhook_url:
            return
        
        # Build message based on event type
        if event_name == "search_completed":
            self._send_search_notification(data)
        elif event_name == "rewrite_completed":
            self._send_rewrite_notification(data)
        elif event_name == "ai_request_completed":
            self._send_ai_notification(data)
        elif event_name == "file_saved":
            self._send_file_saved_notification(data)
    
    def _send_slack_message(self, text, blocks=None):
        """
        Send message to Slack webhook.
        
        Args:
            text: Plain text message (fallback)
            blocks: List of Slack block objects
        """
        try:
            import requests
            
            payload = {"text": text}
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"[Slack Plugin] Failed to send notification: {response.status_code}")
                
        except Exception as e:
            print(f"[Slack Plugin] Error sending notification: {e}")
    
    def _send_search_notification(self, data):
        """Send notification for search completion."""
        query = data.get("query", "Unknown")
        results_count = len(data.get("results", []))
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self._send_slack_message(
            text=f"🔍 Search completed: {results_count} results for '{query}'",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔍 Search Completed*\n\n"
                                f"*Query:* `{query}`\n"
                                f"*Results:* {results_count} matches\n"
                                f"*Time:* {timestamp}"
                    }
                }
            ]
        )
    
    def _send_rewrite_notification(self, data):
        """Send notification for rewrite completion."""
        input_path = data.get("input_path", "Unknown")
        output_path = data.get("output_path", "Unknown")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self._send_slack_message(
            text=f"✏️ JSON rewrite completed: {Path(input_path).name}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*✏️ JSON Rewrite Completed*\n\n"
                                f"*Input:* `{Path(input_path).name}`\n"
                                f"*Output:* `{Path(output_path).name}`\n"
                                f"*Time:* {timestamp}"
                    }
                }
            ]
        )
    
    def _send_ai_notification(self, data):
        """Send notification for AI processing completion."""
        prompt = data.get("prompt", "Unknown")[:100]  # Truncate
        response_length = len(data.get("response", ""))
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self._send_slack_message(
            text=f"🤖 AI processing completed",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🤖 AI Processing Completed*\n\n"
                                f"*Prompt:* {prompt}...\n"
                                f"*Response Length:* {response_length} chars\n"
                                f"*Time:* {timestamp}"
                    }
                }
            ]
        )
    
    def _send_file_saved_notification(self, data):
        """Send notification for file save."""
        path = data.get("path", "Unknown")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self._send_slack_message(
            text=f"💾 File saved: {Path(path).name}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*💾 File Saved*\n\n"
                                f"*File:* `{Path(path).name}`\n"
                                f"*Time:* {timestamp}"
                    }
                }
            ]
        )
