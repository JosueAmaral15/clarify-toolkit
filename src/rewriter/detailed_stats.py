"""Detailed statistics tracking for JSON operations (Sprint B Feature #3 v2.9.31)."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DetailedStatEntry:
    """Single entry in detailed statistics.
    
    Attributes:
        operation: Type of operation (dedupe, eliminate, numeric_keys, etc.)
        original_key: Key that was removed/replaced
        kept_key: Key that was kept (if duplicate)
        similarity: Similarity percentage (for duplicate detection, 0-100)
        line_numbers: Line numbers involved (original, kept)
        count: Number of items affected by this operation
        details: Additional context (optional)
    """
    operation: str
    original_key: str
    kept_key: str = ""
    similarity: float = 0.0
    line_numbers: str = ""
    count: int = 1
    details: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            'operation': self.operation,
            'original_key': self.original_key,
            'kept_key': self.kept_key,
            'similarity': f"{self.similarity:.1f}%" if self.similarity > 0 else "N/A",
            'line_numbers': self.line_numbers,
            'count': self.count,
            'details': self.details
        }


class DetailedStatsCollector:
    """Collects detailed statistics during JSON operations.
    
    Usage:
        collector = DetailedStatsCollector()
        collector.add_entry('dedupe', 'root.user.name', 'root.admin.name', 100.0, '10, 25')
        entries = collector.get_entries()
    """
    
    def __init__(self):
        self.entries: List[DetailedStatEntry] = []
        self.enabled = False
    
    def enable(self):
        """Enable detailed statistics collection."""
        self.enabled = True
    
    def disable(self):
        """Disable detailed statistics collection."""
        self.enabled = False
    
    def add_entry(
        self,
        operation: str,
        original_key: str,
        kept_key: str = "",
        similarity: float = 0.0,
        line_numbers: str = "",
        count: int = 1,
        details: str = ""
    ):
        """Add a new entry to detailed statistics."""
        if not self.enabled:
            return
        
        entry = DetailedStatEntry(
            operation=operation,
            original_key=original_key,
            kept_key=kept_key,
            similarity=similarity,
            line_numbers=line_numbers,
            count=count,
            details=details
        )
        self.entries.append(entry)
    
    def get_entries(self) -> List[DetailedStatEntry]:
        """Get all collected entries."""
        return self.entries
    
    def clear(self):
        """Clear all entries."""
        self.entries.clear()
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary counts by operation type."""
        summary = {}
        for entry in self.entries:
            op = entry.operation
            summary[op] = summary.get(op, 0) + entry.count
        return summary


# Global collector instance (can be replaced with thread-local if needed)
_global_collector = DetailedStatsCollector()


def get_global_collector() -> DetailedStatsCollector:
    """Get the global detailed stats collector."""
    return _global_collector
