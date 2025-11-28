"""
UI module for Clarify.

Contains UI components for threading and processing feedback.
"""
from .thread_manager import ThreadManager, FeatureType, thread_manager
from .processing_modal import ProcessingModal, MinimalProcessingModal

__all__ = [
    "ThreadManager",
    "FeatureType", 
    "thread_manager",
    "ProcessingModal",
    "MinimalProcessingModal"
]
