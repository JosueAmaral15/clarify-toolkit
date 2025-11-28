# 📊 Progress Bar System (v2.5.0)

## Overview

The progress bar system provides real-time visual feedback for all processing operations in Clarify. Each operation (search, replace, insert) runs in a separate thread and displays its progress at the bottom of the main window.

## Key Features

### 1. **Non-Blocking Execution**
- All operations run in separate threads from the GUI
- The GUI remains responsive during long processes
- Multiple operations can run simultaneously

### 2. **Individual Progress Bars**
- Each operation has its own progress bar
- Shows real-time progress (current file, percentage)
- Can be expanded to see complete details

### 3. **Smart Management**
- Bars appear automatically when processing starts
- Progress area hides when no active tasks
- Automatic scroll to manage multiple bars

### 4. **Expanded Details Window**
- Click "↗" button to expand details
- Shows complete processing log
- Allows canceling operation in progress
- Can be minimized back to compact bar

## User Interface

### Location

Progress bars appear at the **bottom of the main window**, below the main tabs (Search/Replace and Insert).

```
┌─────────────────────────────────────────┐
│  [Search/Replace] [Insert]              │  ← Main tabs
│                                          │
│  [Active panel content]                 │
│                                          │
├─────────────────────────────────────────┤
│  Active Tasks (2)                    [▼]│  ← Header (collapsible)
│  ┌─────────────────────────────────┐   │
│  │ Search: pattern  [↗] [✖]        │   │  ← Bar 1
│  │ ████████░░░░░░░░░░ 45%          │   │
│  │ Processing: file50.py           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ Insert: text     [↗] [✖]        │   │  ← Bar 2
│  │ ████████████████░░ 80%          │   │
│  │ Processing: file80.py           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Progress Bar Components

Each bar contains:

1. **Task Name**: Operation identifier (e.g., "Search: pattern")
2. **Expand Button (↗)**: Opens window with complete details
3. **Close Button (✖)**: Removes bar from interface
4. **Progress Bar**: Visual indicator of completion percentage
5. **Status**: Message about current file/action being processed

### Expanded Details Window

When clicking the "↗" button, a modal window opens showing:

```
┌────────────────────────────────────────────┐
│  Progress Details - Search: pattern        │
├────────────────────────────────────────────┤
│  Search: pattern                           │
│  ████████████████████ 75%                  │
│  Progress: 75/100 (75.0%) - file75.py     │
│                                            │
│  Processing Details:                       │
│  ┌────────────────────────────────────────┐│
│  │ [10:30:15] Processing: file1.py        ││
│  │ [10:30:16] Processing: file2.py        ││
│  │ [10:30:17] Processing: file3.py        ││
│  │ ...                                    ││
│  │ [10:30:45] Processing: file75.py       ││
│  └────────────────────────────────────────┘│
│                                            │
│  [↓ Minimize to Bar]  [✖ Cancel Task]     │
└────────────────────────────────────────────┘
```

Features:
- **Larger progress bar**: Easier to visualize
- **Detailed log**: Complete history with timestamps
- **Minimize button**: Return to compact bar
- **Cancel button**: Stop the operation

## Features

### Auto-Hide

The system hides automatically when no tasks:

- **No active tasks**: Progress area completely hidden
- **First task started**: Area appears automatically
- **Last task completed/closed**: Area hides again

### Scroll for Multiple Bars

When there are many simultaneous operations:

- Automatic vertical scroll in bars area
- Maximum of ~3-4 bars visible simultaneously
- Scroll to see all active bars

### Collapse/Expand Area

Click **[▼]** button in header to:

- **▼**: Show all progress bars
- **▲**: Hide bars but keep header visible

Useful when you want to reclaim screen space but continue monitoring the number of active tasks.

### Operation Cancellation

Two ways to cancel:

1. **Cancel Button in Details Window**: Stops processing immediately
2. **Thread continues to checkpoint**: Worker checks cancellation flag between files

**Note**: Cancellation is safe - doesn't corrupt data, just stops processing new files.

### Close Bars Manually

Click **[✖]** button to remove a bar from interface:

- Can close completed bars to clean interface
- Can close bars from long operations you don't want to monitor anymore
- Closing doesn't cancel operation (just removes visualization)

## Integration with Operations

### Search Panel

When you click "Search":

1. Search thread starts
2. Progress bar appears: `"Search: <your pattern>"`
3. Progress updates for each file processed
4. On completion: Status changes to "✓ Completed"
5. Results populate the matches tree

### Insert Panel

When you click "Insert" (with line search):

1. Match search thread starts
2. Bar appears: `"Match Search: <your pattern>"`
3. Progress updates during search
4. On completion: Insertions are applied
5. Results show modified files

### Parallel Operations

You can:

- Start a search
- While search runs, start an insertion
- Both operations show independent progress
- Threads don't interfere with each other
- GUI remains responsive

## Technical Architecture

### Main Classes

#### `ProgressBarWidget`

Individual progress bar widget.

**Responsibilities**:
- Display current progress (bar + percentage)
- Show current status/message
- Provide expand/close buttons
- Emit signals when user interacts

**Signals**:
- `expand_requested(task_id)`: User wants to see details
- `close_requested(task_id)`: User wants to close bar
- `cancel_requested(task_id)`: User wants to cancel task

#### `ProgressDetailsDialog`

Modal window with complete details.

**Responsibilities**:
- Display progress in larger format
- Maintain processing log with timestamps
- Allow minimizing back to bar
- Allow canceling operation

**Main methods**:
- `update_progress(current, total, message)`: Updates bar and status
- `add_log(message)`: Adds entry to log

#### `ProgressManager`

Central manager for all bars.

**Responsibilities**:
- Create and destroy progress bars
- Manage area visibility
- Provide scroll when necessary
- Maintain active tasks count

**Main methods**:
- `add_task(task_id, task_name)`: Creates new bar, returns widget
- `remove_task(task_id)`: Removes bar from system
- `get_task_widget(task_id)`: Gets widget reference

### Workers (Threads)

#### `SearchWorker`

Runs in separate thread for searches.

**New Signals** (v2.5.0):
- `progress_detailed(int, int, str)`: (current, total, message)

**Flow**:
1. Collects list of files to process (to know total)
2. For each file:
   - Emits `progress_detailed` with (index, total, path)
   - Processes file
3. Emits `done` with final results

### Panel Integration

#### `SearchReplacePanel` and `InsertPanel`

**Modifications** (v2.5.0):

1. **Constructor**: Accepts `progress_manager` parameter
2. **When starting search**:
   - Generates unique `task_id` (UUID)
   - Calls `progress_manager.add_task()`
   - Stores reference to created `ProgressBarWidget`
3. **During processing**:
   - Connects `worker.progress_detailed` to update method
   - Updates bar via `widget.update_progress()`
   - Adds logs via `widget.add_log()`
4. **On completion**:
   - Marks bar as complete: `widget.set_complete(success=True)`
   - Doesn't remove automatically (user closes manually)

**Cancellation**:
- Connects `widget.cancel_requested` to `worker.cancel()`
- Worker checks flag between files and stops processing

## Use Cases

### 1. Monitor Long Search

**Situation**: Search in large directory (~10,000 files)

**Flow**:
1. Start search
2. Bar appears showing progress
3. See current file being processed
4. Expand to see log if desired
5. Wait for completion
6. Close bar when no longer needed

### 2. Parallel Operations

**Situation**: Multiple simultaneous searches in different directories

**Flow**:
1. Start first search (Bar 1 appears)
2. Switch to second directory
3. Start second search (Bar 2 appears)
4. Both run independently
5. Scroll to see all bars

### 3. Cancel Long Operation

**Situation**: Search is taking longer than expected

**Flow**:
1. Click "↗" to expand details
2. Review log - see many large files
3. Click "✖ Cancel Task"
4. Operation stops after current file
5. Bar shows "✖ Failed" (cancelled)

### 4. Clean Interface

**Situation**: Many accumulated completed bars

**Flow**:
1. Click "✖" on each completed bar
2. Bars disappear
3. Progress area hides when last bar is closed

## Settings and Limits

### System Limits

- **Maximum log**: 1000 lines per task (prevents excessive memory usage)
- **Maximum area height**: ~250px (about 3-4 visible bars)
- **Message truncation**: Long paths are cut to 60 characters

### Performance

- **Minimal overhead**: Signal emission is very light
- **GUI doesn't freeze**: Separate threads ensure responsiveness
- **Efficient updating**: One emission per file (not per line)

## Known Issues and Solutions

### Issue: Bar doesn't update

**Cause**: Worker isn't emitting `progress_detailed`

**Solution**: Verify worker is connected correctly:
```python
worker.progress_detailed.connect(self._on_progress_detailed)
```

### Issue: Cancellation doesn't work

**Cause**: Worker doesn't check `_cancel` flag

**Solution**: Worker must check flag regularly:
```python
for item in items:
    if self._cancel:
        break
    # process item
```

### Issue: Multiple bars for same operation

**Cause**: `task_id` is not unique

**Solution**: Use UUID to ensure unique IDs:
```python
import uuid
task_id = f"search_{uuid.uuid4().hex[:8]}"
```

## Version

System introduced in Clarify version **2.5.0**.

## Modified Files

- `src/app.py`:
  - New classes: `ProgressBarWidget`, `ProgressDetailsDialog`, `ProgressManager`
  - `SearchWorker`: New signal `progress_detailed`
  - `SearchReplacePanel`: Integration with `progress_manager`
  - `InsertPanel`: Integration with `progress_manager`
  - `MainWindow`: Addition of `ProgressManager` in UI

## Tests

See `test_progress_system.py` for complete automated tests (12 tests covering all functionalities).

## Future Improvements

Possible improvements for future versions:

1. **Persistence**: Save operation history
2. **Time estimation**: Calculate estimated remaining time
3. **Notifications**: Notify when long operations complete
4. **Prioritization**: Allow pausing/resuming operations
5. **Statistics**: Show processing speed (files/second)

## Feedback

If you have suggestions for improvements to the progress system, please contact the developers.
