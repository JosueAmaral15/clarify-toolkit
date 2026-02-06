# Multi-AI Coordination Setup - COM8 (Programmer #8)

**Date**: 2026-01-22  
**Programmer**: #8 (Josué Amaral)  
**Protocol**: Simplicity Protocol 3 v4.5 - Option A (Shared Filesystem)  

---

## 🎯 Coordination Method Selected: **Option A - Shared Filesystem**

### Why Option A?
- ✅ **tmux unavailable** (Option C requires tmux)
- ✅ **Simplest fallback** (Option B requires orchestrator daemon)
- ✅ **Zero dependencies** (just filesystem)
- ✅ **Works on any system**

### Protocol Fallback Hierarchy
```
Try C (tmux + daemon) → FAILED (tmux not installed)
Try B (orchestrator)   → NOT NEEDED (small team, simple coordination)
Use A (shared file)    → ✅ IMPLEMENTED
```

---

## 📁 Coordination File Location

**File**: `/tmp/clarify_ai_coordination.json`

**Purpose**: Central state file for all programmers to coordinate work

**Permissions**: `666` (read/write for all users)

---

## 📋 File Structure

```json
{
  "protocol_version": "1.0",
  "project": "Clarify",
  "coordination_type": "Option A - Shared Filesystem",
  "created_at": "ISO8601 timestamp",
  "agents": {
    "COM8": {
      "programmer_id": 8,
      "name": "Programmer #8",
      "status": "active|idle|blocked",
      "current_task": "Description of current work",
      "last_activity": "ISO8601 timestamp",
      "worktree": "clarify-COM8",
      "branch": "branch-name",
      "completed_tasks": ["list of finished tasks"],
      "current_files": ["files currently editing"],
      "waiting_for": null | "COM1" | "COM2" (if blocked),
      "notes": "Any additional info"
    }
  },
  "messages": [
    {
      "timestamp": "ISO8601",
      "from": "COM8",
      "to": "ALL|COM1|COM2|...",
      "type": "info|question|blocked|complete",
      "message": "Text message"
    }
  ],
  "task_board": {
    "in_progress": [{"task": "...", "assignee": "COMx"}],
    "blocked": [{"task": "...", "assignee": "COMx", "blocking_reason": "..."}],
    "completed": [{"task": "...", "assignee": "COMx", "completed_at": "..."}]
  }
}
```

---

## 🔄 Usage Protocol

### Before Starting Work
1. **Read coordination file**:
   ```bash
   cat /tmp/clarify_ai_coordination.json
   ```

2. **Check for conflicts**:
   - Is someone else working on the same files?
   - Are there messages for you?
   - Are you blocking someone?

3. **Update your status**:
   ```bash
   # Update agent.status, agent.current_task, agent.last_activity
   ```

### During Work
1. **Update status periodically** (every major step)
2. **Add messages** when:
   - You need something from another programmer
   - You complete a task that unblocks others
   - You discover a conflict or issue

### After Completing Work
1. **Update status** to "idle"
2. **Move task** from "in_progress" to "completed"
3. **Add completion message**
4. **Commit coordination file** (optional):
   ```bash
   cp /tmp/clarify_ai_coordination.json ./AI_COORDINATION_LOG.json
   git add AI_COORDINATION_LOG.json
   git commit -m "docs: Update coordination log - COM8 completed Phase 4"
   ```

---

## 🛠️ Helper Commands

### Read Current State
```bash
cat /tmp/clarify_ai_coordination.json | jq .
```

### Check Messages for COM8
```bash
cat /tmp/clarify_ai_coordination.json | jq '.messages[] | select(.to == "COM8" or .to == "ALL")'
```

### Update COM8 Status
```bash
# Use Python/jq to update JSON (example with jq):
jq '.agents.COM8.status = "working" | .agents.COM8.current_task = "New task" | .agents.COM8.last_activity = "2026-01-22T20:50:00Z"' /tmp/clarify_ai_coordination.json > /tmp/temp.json && mv /tmp/temp.json /tmp/clarify_ai_coordination.json
```

### Add Message
```bash
# Python helper script recommended for complex updates
python3 << 'EOF'
import json
from datetime import datetime

with open('/tmp/clarify_ai_coordination.json', 'r') as f:
    data = json.load(f)

data['messages'].append({
    'timestamp': datetime.now().isoformat() + 'Z',
    'from': 'COM8',
    'to': 'ALL',
    'type': 'info',
    'message': 'Your message here'
})

with open('/tmp/clarify_ai_coordination.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Message added!")
EOF
```

---

## 🤝 Coordination Rules (MANDATORY)

1. **ALWAYS read coordination file** before starting work
2. **NEVER modify files** another programmer is working on
3. **UPDATE status immediately** when starting/finishing tasks
4. **COMMUNICATE via messages** - don't assume others know your state
5. **RESOLVE conflicts early** - ask questions if unclear
6. **RESPECT work boundaries** - each programmer has their worktree

---

## 🎓 Example Scenarios

### Scenario 1: COM8 starts new task
```json
{
  "agents": {
    "COM8": {
      "status": "active",
      "current_task": "Implement feature XYZ",
      "current_files": ["src/feature_xyz.py"],
      "last_activity": "2026-01-22T21:00:00Z"
    }
  }
}
```

### Scenario 2: COM8 blocked by COM3
```json
{
  "agents": {
    "COM8": {
      "status": "blocked",
      "current_task": "Write tests for feature XYZ",
      "waiting_for": "COM3",
      "notes": "Waiting for COM3 to finish feature_xyz.py implementation"
    }
  },
  "messages": [
    {
      "from": "COM8",
      "to": "COM3",
      "type": "blocked",
      "message": "Need feature_xyz.py to be committed before I can write tests"
    }
  ]
}
```

### Scenario 3: COM8 completes task
```json
{
  "agents": {
    "COM8": {
      "status": "idle",
      "current_task": null,
      "completed_tasks": ["Feature XYZ implementation", "Feature XYZ tests"]
    }
  },
  "messages": [
    {
      "from": "COM8",
      "to": "ALL",
      "type": "complete",
      "message": "Feature XYZ complete with tests. Ready for review."
    }
  ],
  "task_board": {
    "completed": [
      {"task": "Feature XYZ", "assignee": "COM8", "completed_at": "2026-01-22T21:30:00Z"}
    ]
  }
}
```

---

## ✅ Setup Complete - COM8 Ready

**Status**: ✅ Coordination system initialized  
**File**: `/tmp/clarify_ai_coordination.json`  
**Method**: Option A (Shared Filesystem)  
**COM8**: Active and ready for collaboration  

**Next Steps**:
1. Other programmers should read this file
2. Other programmers should add their agent entries
3. Start coordinating through messages and status updates

---

## 📚 References

- Protocol documentation: `/tmp/multi_ai_communication_en.md`
- Simplicity Protocol 3 v4.5
- Clarify project root: `clarify-COM8/`
