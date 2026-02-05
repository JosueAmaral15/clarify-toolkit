# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
# pylint: disable=import-outside-toplevel  # Avoid circular imports
"""
Calculator Memory Manager for Clarify
Manages memory slots for storing JSON result sets with statistics.

Author: Josué Amaral
Date: 2025/12/22
Version: 2.9.98
"""

import json
from typing import Dict, Any, Optional, List
from PySide6.QtCore import QSettings
from .statistics_manager import StatisticsManager


class CalculatorMemory:
    """
    Manages memory slots for Calculator with statistics tracking.

    Supports 5 memory slots (A, B, C, D, E) for storing JSON result sets.
    Each slot stores: data (JSON), stats (computed statistics), metadata (source, timestamp).
    """

    SLOT_NAMES = ['A', 'B', 'C', 'D', 'E']
    MAX_SLOTS = 5

    def __init__(self):
        """Initialize CalculatorMemory with QSettings for persistence."""
        self.settings = QSettings("Clarify", "CalculatorMemory")
        self._slots: Dict[str, Dict[str, Any]] = {}
        self._load_slots()

    def _load_slots(self):
        """Load slots from QSettings (restore previous session)."""
        for slot_name in self.SLOT_NAMES:
            stored_data = self.settings.value(f"slot_{slot_name}", None)
            if stored_data:
                try:
                    # QSettings stores as string, parse JSON
                    slot_dict = json.loads(stored_data)
                    self._slots[slot_name] = slot_dict
                except (json.JSONDecodeError, TypeError):
                    # Invalid data, skip this slot
                    self._slots[slot_name] = None
            else:
                self._slots[slot_name] = None

    def _save_slot(self, slot_name: str):
        """Save single slot to QSettings."""
        if slot_name in self._slots and self._slots[slot_name]:
            # Serialize to JSON string for QSettings
            self.settings.setValue(f"slot_{slot_name}", json.dumps(self._slots[slot_name]))
        else:
            self.settings.remove(f"slot_{slot_name}")

    def store_result(self, slot_name: str, data: Any, source: str = "Unknown") -> bool:
        """
        Store result in memory slot with statistics.

        Args:
            slot_name: Slot identifier (A, B, C, D, E)
            data: JSON data to store (dict/list)
            source: Source description (e.g., "Set Operations Intersection")

        Returns:
            True if stored successfully, False otherwise
        """
        if slot_name not in self.SLOT_NAMES:
            return False

        # Calculate statistics using StatisticsManager
        stats = StatisticsManager.calculate_statistics(data)

        # Store slot data
        self._slots[slot_name] = {
            'data': data,
            'stats': stats,
            'source': source,
            'timestamp': self._get_timestamp()
        }

        # Persist to QSettings
        self._save_slot(slot_name)
        return True

    def recall_result(self, slot_name: str) -> Optional[Any]:
        """
        Recall data from memory slot.

        Args:
            slot_name: Slot identifier (A, B, C, D, E)

        Returns:
            Stored JSON data or None if slot empty
        """
        if slot_name not in self.SLOT_NAMES:
            return None

        slot = self._slots.get(slot_name)
        return slot['data'] if slot else None

    def get_slot_info(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete slot information (data + stats + metadata).

        Args:
            slot_name: Slot identifier (A, B, C, D, E)

        Returns:
            Dict with data/stats/source/timestamp or None if empty
        """
        if slot_name not in self.SLOT_NAMES:
            return None

        return self._slots.get(slot_name)

    def get_slot_stats(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for slot.

        Args:
            slot_name: Slot identifier (A, B, C, D, E)

        Returns:
            Stats dict or None if slot empty
        """
        slot = self._slots.get(slot_name)
        return slot['stats'] if slot else None

    def clear_slot(self, slot_name: str) -> bool:
        """
        Clear memory slot.

        Args:
            slot_name: Slot identifier (A, B, C, D, E)

        Returns:
            True if cleared, False if slot invalid
        """
        if slot_name not in self.SLOT_NAMES:
            return False

        self._slots[slot_name] = None
        self.settings.remove(f"slot_{slot_name}")
        return True

    def clear_all_slots(self):
        """Clear all memory slots."""
        for slot_name in self.SLOT_NAMES:
            self.clear_slot(slot_name)

    def get_all_slots_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all slots (for table display).

        Returns:
            List of dicts with slot_name, source, stats (or None if empty)
        """
        summary = []
        for slot_name in self.SLOT_NAMES:
            slot = self._slots.get(slot_name)
            if slot:
                summary.append({
                    'slot_name': slot_name,
                    'source': slot['source'],
                    'timestamp': slot['timestamp'],
                    'stats': slot['stats']
                })
            else:
                summary.append({
                    'slot_name': slot_name,
                    'source': None,
                    'timestamp': None,
                    'stats': None
                })
        return summary

    def is_slot_empty(self, slot_name: str) -> bool:
        """Check if slot is empty."""
        return self._slots.get(slot_name) is None

    def get_occupied_slots(self) -> List[str]:
        """Get list of occupied slot names."""
        return [name for name in self.SLOT_NAMES if not self.is_slot_empty(name)]

    def compare_slots(self, slot1: str, slot2: str) -> Optional[Dict[str, Any]]:
        """
        Compare statistics between two slots.

        Args:
            slot1: First slot name
            slot2: Second slot name

        Returns:
            Dict with slot1_stats, slot2_stats, differences or None if invalid
        """
        if slot1 not in self.SLOT_NAMES or slot2 not in self.SLOT_NAMES:
            return None

        stats1 = self.get_slot_stats(slot1)
        stats2 = self.get_slot_stats(slot2)

        if not stats1 or not stats2:
            return None

        # Calculate differences
        differences = {
            'total_keys_diff': stats2['total_keys'] - stats1['total_keys'],
            'unique_keys_diff': stats2['unique_keys'] - stats1['unique_keys'],
            'size_diff': stats2['size_bytes'] - stats1['size_bytes'],
            'depth_diff': stats2['max_depth'] - stats1['max_depth']
        }

        return {
            'slot1': slot1,
            'slot2': slot2,
            'slot1_stats': stats1,
            'slot2_stats': stats2,
            'differences': differences
        }

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
