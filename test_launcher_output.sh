#!/bin/bash
cd "/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify-COM3-study"

echo "Testing clarify.sh launcher..."
echo "Expected: App should launch and show GUI"
echo ""

# Run launcher in background
./clarify.sh > /tmp/clarify_launch.log 2>&1 &
LAUNCHER_PID=$!
echo "Launcher started with PID: $LAUNCHER_PID"

# Wait a bit for app to initialize
sleep 3

# Check if process is running
if ps -p $LAUNCHER_PID > /dev/null 2>&1; then
    echo "✓ Launcher is running"
    
    # Check for Clarify process
    if pgrep -f "python3 -m src" > /dev/null 2>&1; then
        echo "✓ Clarify app process detected"
        CLARIFY_PID=$(pgrep -f "python3 -m src")
        echo "  Clarify PID: $CLARIFY_PID"
        
        echo ""
        echo "Launcher output:"
        cat /tmp/clarify_launch.log
        
        echo ""
        echo "✅ LAUNCHER TEST PASSED!"
        echo "App is running. Terminating for test..."
        
        # Kill the app
        kill $CLARIFY_PID 2>/dev/null
        wait $LAUNCHER_PID 2>/dev/null
    else
        echo "✗ Clarify app not detected"
        echo "Launcher output:"
        cat /tmp/clarify_launch.log
    fi
else
    echo "✗ Launcher exited"
    echo "Exit code: $?"
    echo "Launcher output:"
    cat /tmp/clarify_launch.log
fi

rm -f /tmp/clarify_launch.log
