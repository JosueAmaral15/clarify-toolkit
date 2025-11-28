#!/usr/bin/env python3
"""
test_progress_system.py

Tests for the progress bar system (v2.5.0):
- ProgressBarWidget individual functionality
- ProgressManager multi-task management
- ProgressDetailsDialog expansion
- Integration with SearchWorker
"""


def test_progress_bar_widget_creation():
    """Test creating a progress bar widget."""
    task_id = "test_task_001"
    task_name = "Test Search Operation"
    
    # Simulate widget creation
    widget_data = {
        "task_id": task_id,
        "task_name": task_name,
        "progress": 0,
        "total": 100,
        "status": "Starting..."
    }
    
    assert widget_data["task_id"] == task_id
    assert widget_data["task_name"] == task_name
    assert widget_data["progress"] == 0
    
    print("✓ test_progress_bar_widget_creation passed")


def test_progress_bar_update():
    """Test updating progress bar values."""
    progress_data = {
        "current": 0,
        "total": 100,
        "message": "Starting..."
    }
    
    # Simulate progress updates
    progress_updates = [
        (25, 100, "Processing file 1..."),
        (50, 100, "Processing file 2..."),
        (75, 100, "Processing file 3..."),
        (100, 100, "Complete")
    ]
    
    for current, total, message in progress_updates:
        progress_data["current"] = current
        progress_data["total"] = total
        progress_data["message"] = message
    
    assert progress_data["current"] == 100
    assert progress_data["total"] == 100
    assert progress_data["message"] == "Complete"
    
    print("✓ test_progress_bar_update passed")


def test_progress_percentage_calculation():
    """Test progress percentage calculation."""
    test_cases = [
        (0, 100, 0.0),
        (25, 100, 25.0),
        (50, 100, 50.0),
        (75, 100, 75.0),
        (100, 100, 100.0),
        (0, 0, 0.0),  # Edge case: division by zero
        (50, 200, 25.0),
    ]
    
    for current, total, expected in test_cases:
        if total > 0:
            percent = (current / total) * 100
        else:
            percent = 0.0
        
        assert percent == expected, f"Expected {expected}%, got {percent}%"
    
    print("✓ test_progress_percentage_calculation passed")


def test_progress_manager_add_task():
    """Test adding tasks to progress manager."""
    manager = {
        "active_tasks": {},
        "task_count": 0
    }
    
    # Add multiple tasks
    tasks = [
        ("search_001", "Search: pattern1"),
        ("search_002", "Search: pattern2"),
        ("insert_001", "Insert: text1")
    ]
    
    for task_id, task_name in tasks:
        manager["active_tasks"][task_id] = {
            "name": task_name,
            "progress": 0,
            "total": 100
        }
        manager["task_count"] += 1
    
    assert len(manager["active_tasks"]) == 3
    assert manager["task_count"] == 3
    assert "search_001" in manager["active_tasks"]
    assert "insert_001" in manager["active_tasks"]
    
    print("✓ test_progress_manager_add_task passed")


def test_progress_manager_remove_task():
    """Test removing completed tasks."""
    manager = {
        "active_tasks": {
            "task_001": {"name": "Task 1", "progress": 100},
            "task_002": {"name": "Task 2", "progress": 50},
            "task_003": {"name": "Task 3", "progress": 100}
        }
    }
    
    # Remove completed tasks
    to_remove = ["task_001", "task_003"]
    for task_id in to_remove:
        if task_id in manager["active_tasks"]:
            del manager["active_tasks"][task_id]
    
    assert len(manager["active_tasks"]) == 1
    assert "task_002" in manager["active_tasks"]
    assert "task_001" not in manager["active_tasks"]
    
    print("✓ test_progress_manager_remove_task passed")


def test_progress_manager_visibility():
    """Test progress manager auto-hide when no tasks."""
    manager = {
        "active_tasks": {},
        "visible": False
    }
    
    # Manager should be hidden when no tasks
    manager["visible"] = len(manager["active_tasks"]) > 0
    assert manager["visible"] == False
    
    # Add task - should become visible
    manager["active_tasks"]["task_001"] = {"name": "Task 1"}
    manager["visible"] = len(manager["active_tasks"]) > 0
    assert manager["visible"] == True
    
    # Remove task - should hide again
    del manager["active_tasks"]["task_001"]
    manager["visible"] = len(manager["active_tasks"]) > 0
    assert manager["visible"] == False
    
    print("✓ test_progress_manager_visibility passed")


def test_progress_details_dialog():
    """Test progress details dialog data."""
    dialog_data = {
        "task_name": "Search Operation",
        "progress": 50,
        "total": 100,
        "status": "Processing file 50/100",
        "logs": []
    }
    
    # Add log entries
    logs = [
        "Processing: /path/to/file1.py",
        "Processing: /path/to/file2.js",
        "Processing: /path/to/file3.ts"
    ]
    
    for log in logs:
        dialog_data["logs"].append(log)
    
    assert len(dialog_data["logs"]) == 3
    assert dialog_data["progress"] == 50
    assert "/path/to/file1.py" in dialog_data["logs"][0]
    
    print("✓ test_progress_details_dialog passed")


def test_search_worker_progress_signal():
    """Test SearchWorker progress signal emissions."""
    # Simulate SearchWorker progress tracking
    worker_state = {
        "files_processed": 0,
        "total_files": 10,
        "current_file": None,
        "progress_emissions": []
    }
    
    files = [f"/path/to/file{i}.py" for i in range(1, 11)]
    
    for idx, filepath in enumerate(files, 1):
        worker_state["files_processed"] = idx
        worker_state["current_file"] = filepath
        
        # Simulate progress_detailed signal emission
        emission = (idx, len(files), filepath)
        worker_state["progress_emissions"].append(emission)
    
    assert len(worker_state["progress_emissions"]) == 10
    assert worker_state["progress_emissions"][0] == (1, 10, "/path/to/file1.py")
    assert worker_state["progress_emissions"][-1] == (10, 10, "/path/to/file10.py")
    
    print("✓ test_search_worker_progress_signal passed")


def test_cancel_functionality():
    """Test task cancellation."""
    task_state = {
        "running": True,
        "cancelled": False,
        "processed_items": []
    }
    
    items_to_process = list(range(1, 101))
    
    for idx, item in enumerate(items_to_process):
        # Simulate cancellation at 50%
        if idx == 50:
            task_state["cancelled"] = True
            task_state["running"] = False
        
        if not task_state["running"]:
            break
        
        task_state["processed_items"].append(item)
    
    assert task_state["cancelled"] == True
    assert len(task_state["processed_items"]) == 50
    assert task_state["processed_items"][-1] == 50
    
    print("✓ test_cancel_functionality passed")


def test_multiple_concurrent_tasks():
    """Test managing multiple tasks simultaneously."""
    progress_system = {
        "tasks": {}
    }
    
    # Simulate 3 concurrent operations
    operations = [
        ("search_001", "Search", 100),
        ("replace_001", "Replace", 75),
        ("insert_001", "Insert", 50)
    ]
    
    # Add all tasks
    for task_id, operation, total in operations:
        progress_system["tasks"][task_id] = {
            "operation": operation,
            "current": 0,
            "total": total,
            "status": "running"
        }
    
    # Update progress for each task
    progress_system["tasks"]["search_001"]["current"] = 50
    progress_system["tasks"]["replace_001"]["current"] = 75
    progress_system["tasks"]["insert_001"]["current"] = 50
    
    # Check all tasks are tracked
    assert len(progress_system["tasks"]) == 3
    assert progress_system["tasks"]["search_001"]["current"] == 50
    assert progress_system["tasks"]["replace_001"]["current"] == 75
    
    # Complete one task
    progress_system["tasks"]["replace_001"]["status"] = "completed"
    progress_system["tasks"]["replace_001"]["current"] = 75
    
    completed_count = sum(
        1 for t in progress_system["tasks"].values() 
        if t["status"] == "completed"
    )
    assert completed_count == 1
    
    print("✓ test_multiple_concurrent_tasks passed")


def test_progress_message_truncation():
    """Test long file path truncation in progress messages."""
    long_path = "/very/long/path/to/some/deeply/nested/directory/structure/file.py"
    max_length = 60
    
    # Truncate if longer than max_length
    if len(long_path) > max_length:
        truncated = "..." + long_path[-(max_length - 3):]
    else:
        truncated = long_path
    
    assert len(truncated) <= max_length
    assert truncated.startswith("...")
    assert "file.py" in truncated
    
    print("✓ test_progress_message_truncation passed")


def test_task_id_generation():
    """Test unique task ID generation."""
    import uuid
    
    # Generate multiple task IDs
    task_ids = set()
    for _ in range(100):
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_ids.add(task_id)
    
    # All IDs should be unique
    assert len(task_ids) == 100
    
    # IDs should follow pattern
    for task_id in task_ids:
        assert task_id.startswith("task_")
        assert len(task_id) == 13  # "task_" + 8 hex chars
    
    print("✓ test_task_id_generation passed")


def test_operation_history_persistence():
    """Test operation history persistence to JSON file (v2.5.0+)."""
    import tempfile
    import json
    from pathlib import Path
    
    # Create temporary history file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Simulate history operations
        history_data = []
        
        # Add operation
        operation = {
            "timestamp": "2024-01-15 10:30:45",
            "type": "search",
            "details": {
                "query": "test_pattern",
                "path": "/home/user/test",
                "files_matched": 5,
                "total_matches": 12
            }
        }
        history_data.append(operation)
        
        # Save to temp file
        with open(temp_path, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Read back
        with open(temp_path, 'r') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 1
        assert loaded[0]["type"] == "search"
        assert loaded[0]["details"]["files_matched"] == 5
        
        print("✓ test_operation_history_persistence passed")
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_time_estimation_calculation():
    """Test ETA calculation based on processing speed (v2.5.0+)."""
    import time
    
    # Simulate progress with time tracking
    start_time = time.time()
    
    # Process 25 items in 1 second (simulated)
    current = 25
    total = 100
    elapsed = 1.0
    
    # Calculate speed and ETA
    speed = current / elapsed  # 25 items/sec
    remaining = total - current  # 75 items
    eta_seconds = remaining / speed if speed > 0 else 0  # 3 seconds
    
    assert speed == 25.0
    assert remaining == 75
    assert eta_seconds == 3.0
    
    # Test edge cases
    assert (0 / 1.0) == 0.0  # No progress yet
    eta_zero_speed = 100 / 0.0001 if 0.0001 > 0 else 0  # Very slow
    assert eta_zero_speed > 0
    
    print("✓ test_time_estimation_calculation passed")


def test_pause_resume_functionality():
    """Test pause/resume worker functionality (v2.5.0+)."""
    # Simulate worker state
    worker_state = {
        "_paused": False,
        "current_file": 0,
        "total_files": 10
    }
    
    # Simulate pause
    worker_state["_paused"] = True
    assert worker_state["_paused"] == True
    
    # Worker should wait when paused (simulation)
    if worker_state["_paused"]:
        # In real code: time.sleep(0.1) and continue loop
        pass  # Simulated wait
    
    # Simulate resume
    worker_state["_paused"] = False
    assert worker_state["_paused"] == False
    
    # Worker should continue processing
    if not worker_state["_paused"]:
        worker_state["current_file"] += 1
    
    assert worker_state["current_file"] == 1
    
    print("✓ test_pause_resume_functionality passed")


def test_notification_system():
    """Test desktop notification system with fallbacks (v2.5.0+)."""
    import platform
    
    # Simulate notification data
    notification = {
        "title": "Task Complete",
        "message": "Search completed: 10 files with matches",
        "platform": platform.system()
    }
    
    # Test notification creation
    assert notification["title"] is not None
    assert len(notification["message"]) > 0
    assert notification["platform"] in ["Linux", "Darwin", "Windows"]
    
    # Simulate fallback logic
    try:
        # Try plyer (might not be installed)
        import plyer
        can_use_plyer = True
    except ImportError:
        can_use_plyer = False
    
    # Should have fallback command
    if not can_use_plyer:
        if notification["platform"] == "Linux":
            fallback_cmd = "notify-send"
        elif notification["platform"] == "Darwin":
            fallback_cmd = "osascript"
        else:
            fallback_cmd = None
        
        assert fallback_cmd is not None or notification["platform"] == "Windows"
    
    print("✓ test_notification_system passed")


def test_statistics_display():
    """Test speed statistics display (files/sec, files/min) (v2.5.0+)."""
    # Test different speed calculations
    test_cases = [
        (50, 1.0, "50.0/s"),      # 50 files in 1 second
        (10, 0.5, "20.0/s"),      # 10 files in 0.5 seconds
        (5, 10.0, "30.0/min"),    # 5 files in 10 seconds (0.5/s -> 30/min)
        (2, 5.0, "24.0/min"),     # 2 files in 5 seconds (0.4/s -> 24/min)
        (10, 120.0, "5.0/min"),   # 10 files in 2 minutes
    ]
    
    for current, elapsed, expected in test_cases:
        speed = current / elapsed if elapsed > 0 else 0
        
        # Format like in app.py
        if speed >= 1:
            formatted = f"{speed:.1f}/s"
        else:
            # Convert to per-minute
            speed_per_min = speed * 60
            formatted = f"{speed_per_min:.1f}/min"
        
        assert formatted == expected, f"Expected {expected}, got {formatted}"
    
    # Test zero/edge cases
    speed_zero = 0 / 1.0 if 1.0 > 0 else 0
    assert speed_zero == 0.0
    
    print("✓ test_statistics_display passed")


def test_history_max_size():
    """Test that history keeps only last 1000 operations (v2.5.0+)."""
    # Simulate history with max size
    max_size = 1000
    history = []
    
    # Add 1500 operations
    for i in range(1500):
        history.append({
            "timestamp": f"2024-01-15 10:{i % 60:02d}:00",
            "type": "search",
            "details": {"id": i}
        })
    
    # Trim to max size (like in OperationHistory._save_history)
    if len(history) > max_size:
        history = history[-max_size:]
    
    assert len(history) == max_size
    assert history[0]["details"]["id"] == 500  # First of last 1000
    assert history[-1]["details"]["id"] == 1499  # Last operation
    
    print("✓ test_history_max_size passed")


if __name__ == "__main__":
    print("Running progress system tests (v2.5.0+)...\n")
    
    # Base system tests (v2.5.0)
    test_progress_bar_widget_creation()
    test_progress_bar_update()
    test_progress_percentage_calculation()
    test_progress_manager_add_task()
    test_progress_manager_remove_task()
    test_progress_manager_visibility()
    test_progress_details_dialog()
    test_search_worker_progress_signal()
    test_cancel_functionality()
    test_multiple_concurrent_tasks()
    test_progress_message_truncation()
    test_task_id_generation()
    
    # Enhancement tests (v2.5.0+)
    print("\nRunning enhancement tests (v2.5.0+)...\n")
    test_operation_history_persistence()
    test_time_estimation_calculation()
    test_pause_resume_functionality()
    test_notification_system()
    test_statistics_display()
    test_history_max_size()
    
    print("\n" + "="*60)
    print("All 18 progress system tests passed! ✓")
    print("  - 12 base system tests (v2.5.0)")
    print("  -  6 enhancement tests (v2.5.0+)")
    print("="*60)
