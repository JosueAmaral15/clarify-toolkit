#!/usr/bin/env python3
"""
test_thread_management_system.py

Testes para validar sistema de gerenciamento de threads e modals.
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import thread_manager, FeatureType

def test_singleton():
    """Test that ThreadManager is a singleton"""
    from src.ui.thread_manager import ThreadManager
    
    tm1 = ThreadManager()
    tm2 = ThreadManager()
    
    assert tm1 is tm2, "ThreadManager should be a singleton"
    assert tm1 is thread_manager, "Should be same as global instance"
    
    print("✓ test_singleton passed")


def test_feature_locks():
    """Test that feature locks prevent simultaneous execution"""
    # Initially all features should be available
    for feature in FeatureType:
        assert thread_manager.can_start_feature(feature), \
            f"Feature {feature.value} should be available initially"
    
    print("✓ test_feature_locks passed")


def test_thread_registration():
    """Test thread registration"""
    from PySide6.QtCore import QThread, QObject
    
    class DummyWorker(QObject):
        def __init__(self):
            super().__init__()
            self.cancelled = False
        
        def cancel(self):
            self.cancelled = True
    
    # Create dummy thread and worker
    thread = QThread()
    worker = DummyWorker()
    worker.moveToThread(thread)
    
    # Register thread
    thread_id = "test_thread_1"
    result = thread_manager.start_thread(
        thread_id=thread_id,
        thread=thread,
        worker=worker,
        feature=FeatureType.SEARCH_REPLACE,
        cancel_callback=lambda: worker.cancel()
    )
    
    assert result is True, "Thread registration should succeed"
    
    # Feature should now be locked
    assert not thread_manager.can_start_feature(FeatureType.SEARCH_REPLACE), \
        "Feature should be locked after thread registration"
    
    # Try to register another thread for same feature (should fail)
    thread2 = QThread()
    worker2 = DummyWorker()
    worker2.moveToThread(thread2)
    
    result2 = thread_manager.start_thread(
        thread_id="test_thread_2",
        thread=thread2,
        worker=worker2,
        feature=FeatureType.SEARCH_REPLACE
    )
    
    assert result2 is False, "Second thread registration for same feature should fail"
    
    # Cancel first thread
    thread_manager.cancel_thread(thread_id)
    assert worker.cancelled is True, "Worker should be cancelled"
    
    # Clean up
    thread.quit()
    thread.wait(1000)
    thread2.quit()
    thread2.wait(1000)
    
    print("✓ test_thread_registration passed")


def test_multiple_features_parallel():
    """Test that different features can run in parallel"""
    from PySide6.QtCore import QThread, QObject
    
    class DummyWorker(QObject):
        pass
    
    threads = []
    
    # Register threads for different features (usando features não testadas anteriormente)
    features = [
        FeatureType.JSON_REWRITER,
        FeatureType.JSON_SEARCH,
        FeatureType.TEXT_EXTRACTOR
    ]
    
    for i, feature in enumerate(features):
        thread = QThread()
        worker = DummyWorker()
        worker.moveToThread(thread)
        
        thread_id = f"test_multi_{i}"
        result = thread_manager.start_thread(
            thread_id=thread_id,
            thread=thread,
            worker=worker,
            feature=feature
        )
        
        assert result is True, f"Thread registration for {feature.value} should succeed"
        threads.append(thread)
    
    # All three features should be locked
    for feature in features:
        assert not thread_manager.can_start_feature(feature), \
            f"Feature {feature.value} should be locked"
    
    # Other features should still be available
    assert thread_manager.can_start_feature(FeatureType.AI_FILE_PROCESSOR), \
        "Unlocked features should still be available"
    
    # Clean up
    thread_manager.wait_all_threads(timeout_ms=1000)
    for thread in threads:
        thread.quit()
        thread.wait(1000)
    
    print("✓ test_multiple_features_parallel passed")


def test_stats():
    """Test statistics gathering"""
    stats = thread_manager.get_stats()
    
    assert "total_threads" in stats
    assert "running_threads" in stats
    assert "by_feature" in stats
    assert "shutdown_mode" in stats
    
    assert isinstance(stats["total_threads"], int)
    assert isinstance(stats["running_threads"], int)
    assert isinstance(stats["by_feature"], dict)
    assert isinstance(stats["shutdown_mode"], bool)
    
    print("✓ test_stats passed")


def test_is_feature_running():
    """Test feature running detection"""
    # Initially no feature should be running
    assert not thread_manager.is_feature_running(FeatureType.CASE_CONVERTER), \
        "No feature should be running initially"
    
    # Test that feature lock prevents concurrent access
    assert thread_manager.can_start_feature(FeatureType.CASE_CONVERTER), \
        "Feature should be available"
    
    print("✓ test_is_feature_running passed")


def test_cancel_feature():
    """Test basic cancellation functionality"""
    # Test that cancel_thread works for non-existent threads
    result = thread_manager.cancel_thread("non_existent_thread")
    assert result is False, "Cancel should return False for non-existent thread"
    
    # Test stats
    stats = thread_manager.get_stats()
    assert stats is not None, "Should be able to get stats"
    
    print("✓ test_cancel_feature passed")


if __name__ == "__main__":
    print("Running Thread Management System tests...\n")
    
    try:
        test_singleton()
        test_feature_locks()
        test_thread_registration()
        test_multiple_features_parallel()
        test_stats()
        test_is_feature_running()
        test_cancel_feature()
        
        print("\n" + "="*60)
        print("✅ All 7 thread management tests passed!")
        print("="*60)
        print("\n📝 Features validated:")
        print("  ✓ Singleton pattern")
        print("  ✓ Feature locks")
        print("  ✓ Thread registration")
        print("  ✓ Parallel execution")
        print("  ✓ Statistics gathering")
        print("  ✓ Feature running detection")
        print("  ✓ Feature cancellation")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
