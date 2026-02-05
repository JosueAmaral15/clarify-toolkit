#!/usr/bin/env python3
"""
tmux Coordinator Daemon
Monitors all tmux panes and coordinates AI work
Based on Simplicity Protocol 3 - Option C
"""

import subprocess
import json
import time
import re
from datetime import datetime
from pathlib import Path

STATE_FILE = "/tmp/tmux_ai_state.json"

def get_tmux_panes():
    """Get all panes in current session"""
    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-F", "#{pane_index}:#{pane_title}"],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            return {}
        
        panes = {}
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                idx, title = line.split(":", 1)
                panes[int(idx)] = title
        return panes
    except Exception as e:
        print(f"⚠️  Error getting panes: {e}")
        return {}

def capture_pane_output(pane_idx, lines=50):
    """Capture recent output from a pane"""
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{pane_idx}", "-S", f"-{lines}"],
            capture_output=True, text=True, check=False
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        print(f"⚠️  Error capturing pane {pane_idx}: {e}")
        return ""

def extract_ai_status(output):
    """Extract AI status from output"""
    status = {
        "working_on": None,
        "status": "idle",
        "branch": None,
        "locked_files": []
    }
    
    # Look for common patterns
    if re.search(r"(refactor|modifying|editing|investigating)", output, re.I):
        status["status"] = "working"
    if re.search(r"(test|testing|pytest)", output, re.I):
        status["status"] = "testing"
    if re.search(r"(lint|linting|checking)", output, re.I):
        status["status"] = "linting"
    if re.search(r"(reading|studying|analyzing)", output, re.I):
        status["status"] = "studying"
    
    # Extract branch
    branch_match = re.search(r"COM[0-9]+-[\w-]+", output)
    if branch_match:
        status["branch"] = branch_match.group(0)
    
    # Extract files being edited
    file_matches = re.findall(r"(src/[\w/]+\.py|tests/[\w/]+\.py|[\w/]+\.js|[\w/]+\.ts)", output)
    status["locked_files"] = list(set(file_matches))[:5]  # Max 5
    
    return status

def update_state(panes_data):
    """Update global state file"""
    state = {
        "updated_at": datetime.now().isoformat(),
        "panes": panes_data,
        "active_programmers": len(panes_data)
    }
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error writing state file: {e}")

def main():
    print("🖥️  tmux Coordinator Daemon Started")
    print(f"   State file: {STATE_FILE}")
    print("   Protocol: Simplicity 3 - Option C")
    print("   Monitoring panes...")
    print()
    
    while True:
        try:
            panes = get_tmux_panes()
            panes_data = {}
            
            for idx, title in panes.items():
                if "Daemon" in title or "daemon" in title.lower():
                    continue  # Skip self
                
                output = capture_pane_output(idx, lines=30)
                status = extract_ai_status(output)
                
                panes_data[f"pane-{idx}"] = {
                    "title": title,
                    "pane_index": idx,
                    **status,
                    "last_update": datetime.now().isoformat()
                }
            
            update_state(panes_data)
            
            # Print status
            now = datetime.now().strftime('%H:%M:%S')
            print(f"\r⏱️  {now} | Active: {len(panes_data)} | ", end="")
            for pane_id, data in panes_data.items():
                print(f"{data['title']}: {data['status']} | ", end="")
            print("  ", end="", flush=True)
            
            time.sleep(5)  # Update every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\n👋 Daemon stopped")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
