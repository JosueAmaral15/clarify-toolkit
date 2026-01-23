#!/bin/bash
# Setup tmux session for multi-AI coordination
# Based on Simplicity Protocol 3 - Option C

SESSION_NAME="clarify-multi-ai"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/tmux_coordinator_daemon.py"

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "✅ Session '$SESSION_NAME' already exists"
    echo "   Attaching to existing session..."
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

echo "🖥️  Creating tmux session: $SESSION_NAME"

# Create tmux session with 4 panes
tmux new-session -d -s "$SESSION_NAME" -n "MultiAI"

# Split into 4 panes (2x2 grid)
tmux split-window -h -t "$SESSION_NAME"
tmux split-window -v -t "$SESSION_NAME:0.0"
tmux split-window -v -t "$SESSION_NAME:0.2"

# Label panes
tmux select-pane -t "$SESSION_NAME:0.0" -T "Programmer-3"
tmux select-pane -t "$SESSION_NAME:0.1" -T "Programmer-6"
tmux select-pane -t "$SESSION_NAME:0.2" -T "Available"
tmux select-pane -t "$SESSION_NAME:0.3" -T "Daemon"

# Start daemon in pane 3
tmux send-keys -t "$SESSION_NAME:0.3" "cd '$SCRIPT_DIR/..' && python3 '$DAEMON_SCRIPT'" C-m

# Set working directory for other panes
for pane in 0 1 2; do
    tmux send-keys -t "$SESSION_NAME:0.$pane" "cd '$SCRIPT_DIR/..'" C-m
done

echo "✅ Session created successfully!"
echo ""
echo "Pane Layout:"
echo "  ┌──────────────┬──────────────┐"
echo "  │ Programmer-3 │ Programmer-6 │"
echo "  ├──────────────┼──────────────┤"
echo "  │ Available    │ Daemon       │"
echo "  └──────────────┴──────────────┘"
echo ""
echo "Commands:"
echo "  - Attach: tmux attach-session -t $SESSION_NAME"
echo "  - Detach: Ctrl+b then d"
echo "  - Switch pane: Ctrl+b then arrow keys"
echo ""

# Attach to session
tmux attach-session -t "$SESSION_NAME"
