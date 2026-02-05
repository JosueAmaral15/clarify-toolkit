#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Venn Diagram Generator for Clarify
Generate Venn diagram data for visualizing set operations results.

Considers KEYS + VALUES (not just keys) for JSON/TOON/BSON comparison.

Author: Josué Amaral
Date: 2025-12-23
Version: v2.9.107
"""

from typing import Dict, List, Any, Tuple


class VennDiagramGenerator:
    """
    Generate Venn diagram data from Set Operations results.

    Supports 2-circle Venn diagrams showing:
    - Only in A (keys+values exclusive to File A or modified values in A)
    - Only in B (keys+values exclusive to File B or modified values in B)
    - A ∩ B (keys+values identical in both files)
    """

    @staticmethod
    def generate(
        diff_result: Dict[str, Any],
        file_a_name: str,
        file_b_name: str,
        comparison_mode: str = "key_value"
    ) -> Dict[str, Any]:
        """
        Generate Venn diagram data from DiffAnalyzer results.

        Args:
            diff_result: Result from DiffAnalyzer.analyze()
                {
                    "only_in_a": {key: value},
                    "only_in_b": {key: value},
                    "common": {key: {"a": value, "b": value}},
                    "modified": {key: {"a": value_a, "b": value_b}}
                }
            file_a_name: Name of File A
            file_b_name: Name of File B
            comparison_mode: Comparison mode (key_value, full_path_value, key_only)

        Returns:
            Dict with Venn diagram data:
            {
                "regions": {
                    "only_a": {
                        "keys": [key1, key2, ...],
                        "count": N,
                        "percentage": X.X,
                        "label": "Only in A",
                        "color": "#c8f7c5"
                    },
                    "only_b": {...},
                    "intersection": {...}
                },
                "total_keys": N,
                "file_a_name": "file.json",
                "file_b_name": "file2.json",
                "comparison_mode": "key_value"
            }
        """
        # Extract keys from each category
        only_a_keys = list(diff_result.get("only_in_a", {}).keys())
        only_b_keys = list(diff_result.get("only_in_b", {}).keys())
        common_keys = list(diff_result.get("common", {}).keys())
        modified_keys = list(diff_result.get("modified", {}).keys())

        # For Venn diagram considering KEYS + VALUES:
        # - Only A: keys exclusive to A (only_in_a) + keys with different values favoring A (modified)
        # - Only B: keys exclusive to B (only_in_b) + keys with different values favoring B (modified)
        # - Intersection: keys with identical values in both (common)

        # Note: modified keys represent keys that exist in both but with DIFFERENT values
        # For Venn diagram, we can either:
        # 1. Split modified between A and B (half each) - not intuitive
        # 2. Exclude modified from Venn (show separately) - more accurate
        # 3. Include modified in "outside intersection" - clearer

        # Going with option 3: modified keys are NOT in intersection (different values)
        # region_only_a_keys = only_a_keys + modified_keys  # Unused - kept for documentation
        # region_only_b_keys = only_b_keys + modified_keys  # Unused - kept for documentation
        # region_intersection_keys = common_keys  # Unused - kept for documentation

        # Calculate total unique keys
        total_keys = len(set(only_a_keys + only_b_keys + common_keys + modified_keys))

        # Calculate counts and percentages
        count_only_a = len(only_a_keys) + len(modified_keys)
        count_only_b = len(only_b_keys) + len(modified_keys)
        count_intersection = len(common_keys)

        percentage_only_a = (count_only_a / total_keys * 100) if total_keys > 0 else 0
        percentage_only_b = (count_only_b / total_keys * 100) if total_keys > 0 else 0
        percentage_intersection = (count_intersection / total_keys * 100) if total_keys > 0 else 0

        # Build Venn diagram data
        venn_data = {
            "regions": {
                "only_a": {
                    "keys": only_a_keys,
                    "modified_keys": modified_keys,  # Keys with different values
                    "count": count_only_a,
                    "percentage": round(percentage_only_a, 1),
                    "label": f"Only in {file_a_name}",
                    "color": "#c8f7c5",  # Light green
                    "description": f"{count_only_a} keys ({percentage_only_a:.1f}%)"
                },
                "only_b": {
                    "keys": only_b_keys,
                    "modified_keys": modified_keys,  # Same modified keys (different perspective)
                    "count": count_only_b,
                    "percentage": round(percentage_only_b, 1),
                    "label": f"Only in {file_b_name}",
                    "color": "#ffcccb",  # Light red
                    "description": f"{count_only_b} keys ({percentage_only_b:.1f}%)"
                },
                "intersection": {
                    "keys": common_keys,
                    "count": count_intersection,
                    "percentage": round(percentage_intersection, 1),
                    "label": f"{file_a_name} ∩ {file_b_name}",
                    "color": "#ffffcc",  # Light yellow
                    "description": f"{count_intersection} keys ({percentage_intersection:.1f}%)"
                }
            },
            "total_keys": total_keys,
            "file_a_name": file_a_name,
            "file_b_name": file_b_name,
            "comparison_mode": comparison_mode,
            "summary": f"Total: {total_keys} keys | A: {count_only_a} | B: {count_only_b} | A∩B: {count_intersection}"
        }

        return venn_data

    @staticmethod
    def get_region_details(
        venn_data: Dict[str, Any],
        region: str,
        diff_result: Dict[str, Any]
    ) -> List[Tuple[str, Any]]:
        """
        Get detailed key-value pairs for a specific region.

        Args:
            venn_data: Venn diagram data from generate()
            region: Region name ('only_a', 'only_b', 'intersection')
            diff_result: Original DiffAnalyzer result

        Returns:
            List of (key, value) tuples for display
        """
        details = []

        if region == "only_a":
            # Keys exclusive to A
            for key in venn_data["regions"]["only_a"]["keys"]:
                value = diff_result["only_in_a"].get(key)
                details.append((key, value))

            # Modified keys (show A's value)
            for key in venn_data["regions"]["only_a"]["modified_keys"]:
                value_a = diff_result["modified"][key]["a"]
                details.append((f"{key} (modified)", value_a))

        elif region == "only_b":
            # Keys exclusive to B
            for key in venn_data["regions"]["only_b"]["keys"]:
                value = diff_result["only_in_b"].get(key)
                details.append((key, value))

            # Modified keys (show B's value)
            for key in venn_data["regions"]["only_b"]["modified_keys"]:
                value_b = diff_result["modified"][key]["b"]
                details.append((f"{key} (modified)", value_b))

        elif region == "intersection":
            # Common keys (show value from A, they're identical in B)
            for key in venn_data["regions"]["intersection"]["keys"]:
                value = diff_result["common"][key]["a"]
                details.append((key, value))

        return details

    @staticmethod
    def format_summary(venn_data: Dict[str, Any]) -> str:
        """
        Format Venn diagram summary as human-readable text.

        Args:
            venn_data: Venn diagram data from generate()

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("=== Venn Diagram Summary ===")
        lines.append(f"File A: {venn_data['file_a_name']}")
        lines.append(f"File B: {venn_data['file_b_name']}")
        lines.append(f"Comparison Mode: {venn_data['comparison_mode']}")
        lines.append(f"Total Keys: {venn_data['total_keys']}")
        lines.append("")

        for _, region_data in venn_data["regions"].items():  # region_name unused
            lines.append(f"- {region_data['label']}: {region_data['description']}")

        lines.append("")
        lines.append(f"Summary: {venn_data['summary']}")

        return "\n".join(lines)

    @staticmethod
    def export_svg(venn_data: Dict[str, Any], output_path: str) -> None:
        """
        Export Venn diagram as SVG file (basic implementation).

        Args:
            venn_data: Venn diagram data from generate()
            output_path: Path to save SVG file
        """
        # SVG parameters
        width = 600
        height = 400
        radius = 120
        center_a_x = width // 2 - 60
        center_a_y = height // 2
        center_b_x = width // 2 + 60
        center_b_y = height // 2

        # Extract data
        only_a = venn_data["regions"]["only_a"]
        only_b = venn_data["regions"]["only_b"]
        intersection = venn_data["regions"]["intersection"]

        # Build SVG
        svg_lines = []
        svg_lines.append(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
        svg_lines.append(f'  <title>Venn Diagram: {venn_data["file_a_name"]} vs {venn_data["file_b_name"]}</title>')

        # Circle A
        svg_lines.append(f'  <circle cx="{center_a_x}" cy="{center_a_y}" r="{radius}" ')
        svg_lines.append(f'    fill="{only_a["color"]}" fill-opacity="0.5" stroke="black" stroke-width="2"/>')

        # Circle B
        svg_lines.append(f'  <circle cx="{center_b_x}" cy="{center_b_y}" r="{radius}" ')
        svg_lines.append(f'    fill="{only_b["color"]}" fill-opacity="0.5" stroke="black" stroke-width="2"/>')

        # Labels
        svg_lines.append(f'  <text x="{center_a_x - 80}" y="{center_a_y}" font-size="14" font-weight="bold">')
        svg_lines.append(f'    {venn_data["file_a_name"]}</text>')

        svg_lines.append(f'  <text x="{center_b_x + 40}" y="{center_b_y}" font-size="14" font-weight="bold">')
        svg_lines.append(f'    {venn_data["file_b_name"]}</text>')

        # Counts
        svg_lines.append(f'  <text x="{center_a_x - 40}" y="{center_a_y + 5}" font-size="18" font-weight="bold">')
        svg_lines.append(f'    {only_a["count"]}</text>')

        svg_lines.append(f'  <text x="{width // 2 - 10}" y="{center_a_y + 5}" font-size="18" font-weight="bold">')
        svg_lines.append(f'    {intersection["count"]}</text>')

        svg_lines.append(f'  <text x="{center_b_x + 30}" y="{center_b_y + 5}" font-size="18" font-weight="bold">')
        svg_lines.append(f'    {only_b["count"]}</text>')

        # Summary
        svg_lines.append(f'  <text x="10" y="{height - 10}" font-size="12">')
        svg_lines.append(f'    {venn_data["summary"]}</text>')

        svg_lines.append('</svg>')

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_lines))
