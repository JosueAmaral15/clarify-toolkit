# Slack Notifications Plugin

Send real-time notifications to Slack channels when Clarify operations complete.

## Features

- 💬 **Real-time Notifications**: Get instant updates in Slack
- ⚙️ **Configurable Events**: Choose which operations trigger notifications
- 🎨 **Rich Formatting**: Beautiful messages with Slack blocks
- 🧪 **Test Mode**: Verify webhook before saving
- 🔒 **Secure**: Uses Slack's official Incoming Webhooks

## Installation

1. Install requests dependency (usually already available):
```bash
pip install requests
```

2. Create a Slack Incoming Webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Create a new webhook for your workspace
   - Copy the webhook URL

3. Enable the plugin in Clarify settings

## Usage

1. **Tools → Integrations → Slack Notifications Settings...**
2. Paste your Slack webhook URL
3. Select which events should trigger notifications:
   - ✅ Search completed
   - ✅ JSON rewrite completed
   - ✅ AI processing completed
   - ✅ File saved
4. Click **Send Test Notification** to verify
5. Click **Save Settings**

## Notification Examples

### Search Completed
```
🔍 Search Completed

Query: `user.email`
Results: 42 matches
Time: 14:23:15
```

### JSON Rewrite Completed
```
✏️ JSON Rewrite Completed

Input: `config.json`
Output: `config_rewritten.json`
Time: 14:25:30
```

### AI Processing Completed
```
🤖 AI Processing Completed

Prompt: Refactor this JSON to use camelCase...
Response Length: 1,234 chars
Time: 14:30:45
```

## Configuration

Settings are saved in QSettings under `plugins/Slack Notifications/`:
- `webhook_url`: Your Slack webhook URL
- `events`: List of enabled events

## Requirements

- Slack workspace with Incoming Webhooks enabled
- Python `requests` library
