"""
Diff Analyzer for Clarify
Analyzes differences between two JSON datasets for visualization.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.99
"""

from typing import Any, Dict
import json


class DiffAnalyzer:
    """
    Analyzes differences between two JSON datasets.

    Categorizes keys/values into:
    - only_in_a: Items unique to first dataset
    - only_in_b: Items unique to second dataset
    - common: Items present in both with same value
    - modified: Items present in both but with different values
    """

    @staticmethod
    def analyze(data_a: Any, data_b: Any, comparison_mode: str = "key_value") -> Dict[str, Any]:
        """
        Analyze differences between two datasets.

        Args:
            data_a: First dataset (dict or list)
            data_b: Second dataset (dict or list)
            comparison_mode: Comparison mode ("key_value", "full_path_value", "key_only")

        Returns:
            Dict with categories: only_in_a, only_in_b, common, modified
        """
        # Flatten both datasets for comparison
        flat_a = DiffAnalyzer._flatten_dict(data_a)
        flat_b = DiffAnalyzer._flatten_dict(data_b)

        keys_a = set(flat_a.keys())
        keys_b = set(flat_b.keys())

        # Categorize keys
        only_in_a = keys_a - keys_b
        only_in_b = keys_b - keys_a
        common_keys = keys_a & keys_b

        # For common keys, check if values differ
        common = {}
        modified = {}

        for key in common_keys:
            val_a = flat_a[key]
            val_b = flat_b[key]

            if comparison_mode == "key_only":
                # Key exists in both = common
                common[key] = {"a": val_a, "b": val_b}
            elif DiffAnalyzer._values_equal(val_a, val_b, comparison_mode):
                common[key] = {"a": val_a, "b": val_b}
            else:
                modified[key] = {"a": val_a, "b": val_b}

        return {
            "only_in_a": {k: flat_a[k] for k in only_in_a},
            "only_in_b": {k: flat_b[k] for k in only_in_b},
            "common": common,
            "modified": modified
        }

    @staticmethod
    def _flatten_dict(data: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        """
        Flatten nested dict/list to dot-notation.

        Args:
            data: Data to flatten (dict, list, or primitive)
            parent_key: Parent key for recursion
            sep: Separator for key concatenation

        Returns:
            Flattened dict with dot-notation keys
        """
        items = {}

        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    items.update(DiffAnalyzer._flatten_dict(v, new_key, sep))
                else:
                    items[new_key] = v
        elif isinstance(data, list):
            for i, v in enumerate(data):
                new_key = f"{parent_key}[{i}]"
                if isinstance(v, (dict, list)):
                    items.update(DiffAnalyzer._flatten_dict(v, new_key, sep))
                else:
                    items[new_key] = v
        else:
            # Primitive value
            items[parent_key] = data

        return items

    @staticmethod
    def _values_equal(val_a: Any, val_b: Any, comparison_mode: str) -> bool:
        """
        Check if two values are equal according to comparison mode.

        Args:
            val_a: First value
            val_b: Second value
            comparison_mode: Comparison mode

        Returns:
            True if values considered equal
        """
        if comparison_mode == "key_only":
            return True  # In key_only mode, all common keys are "equal"

        # For key_value and full_path_value, do strict comparison
        return val_a == val_b

    @staticmethod
    def format_diff_summary(diff_result: Dict[str, Any]) -> str:
        """
        Format diff analysis result as summary text.

        Args:
            diff_result: Result from analyze()

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append("DIFF ANALYSIS SUMMARY")
        lines.append("=" * 50)
        lines.append(f"Only in A:  {len(diff_result['only_in_a'])} items")
        lines.append(f"Only in B:  {len(diff_result['only_in_b'])} items")
        lines.append(f"Common:     {len(diff_result['common'])} items")
        lines.append(f"Modified:   {len(diff_result['modified'])} items")
        lines.append("")
        total_a = (len(diff_result['only_in_a']) +
                   len(diff_result['common']) +
                   len(diff_result['modified']))
        total_b = (len(diff_result['only_in_b']) +
                   len(diff_result['common']) +
                   len(diff_result['modified']))
        lines.append(f"Total keys in A: {total_a}")
        lines.append(f"Total keys in B: {total_b}")

        return "\n".join(lines)

    @staticmethod
    def export_diff_html(diff_result: Dict[str, Any], file_a_name: str, file_b_name: str, output_path: str):
        """
        Export diff analysis as HTML with color highlighting.

        Args:
            diff_result: Result from analyze()
            file_a_name: Name of first file
            file_b_name: Name of second file
            output_path: Output HTML file path
        """
        html_lines = []
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html>")
        html_lines.append("<head>")
        html_lines.append("<meta charset='UTF-8'>")
        html_lines.append(f"<title>Diff: {file_a_name} vs {file_b_name}</title>")
        html_lines.append("<style>")
        html_lines.append("body { font-family: 'Courier New', monospace; font-size: 12px; padding: 20px; }")
        html_lines.append(".container { display: flex; gap: 20px; }")
        html_lines.append(".panel { flex: 1; border: 1px solid #ccc; padding: 10px; background: #f9f9f9; }")
        html_lines.append(".panel h2 { margin-top: 0; }")
        html_lines.append(".only-a { background-color: #c8f7c5; padding: 2px 4px; }")
        html_lines.append(".only-b { background-color: #ffcccb; padding: 2px 4px; }")
        html_lines.append(".common { background-color: #ffffcc; padding: 2px 4px; }")
        html_lines.append(".modified { background-color: #ffd9b3; padding: 2px 4px; }")
        html_lines.append(".key { font-weight: bold; }")
        html_lines.append(".summary { background: #e6f3ff; padding: 15px; margin-bottom: 20px; border-radius: 5px; }")
        html_lines.append("</style>")
        html_lines.append("</head>")
        html_lines.append("<body>")
        html_lines.append(f"<h1>Diff Viewer: {file_a_name} vs {file_b_name}</h1>")

        # Summary
        html_lines.append("<div class='summary'>")
        html_lines.append(f"<strong>Only in A:</strong> {len(diff_result['only_in_a'])} | ")
        html_lines.append(f"<strong>Only in B:</strong> {len(diff_result['only_in_b'])} | ")
        html_lines.append(f"<strong>Common:</strong> {len(diff_result['common'])} | ")
        html_lines.append(f"<strong>Modified:</strong> {len(diff_result['modified'])}")
        html_lines.append("</div>")

        # Side-by-side panels
        html_lines.append("<div class='container'>")

        # Panel A
        html_lines.append("<div class='panel'>")
        html_lines.append(f"<h2>{file_a_name}</h2>")
        html_lines.append("<pre>")

        # Only in A (green)
        for key, value in sorted(diff_result['only_in_a'].items()):
            val_json = json.dumps(value)
            html_lines.append(
                f"<span class='only-a'><span class='key'>{key}:</span> {val_json}</span>"
            )

        # Common (yellow)
        for key, values in sorted(diff_result['common'].items()):
            val_json = json.dumps(values['a'])
            html_lines.append(
                f"<span class='common'><span class='key'>{key}:</span> {val_json}</span>"
            )

        # Modified (orange) - show value from A
        for key, values in sorted(diff_result['modified'].items()):
            val_json = json.dumps(values['a'])
            html_lines.append(
                f"<span class='modified'><span class='key'>{key}:</span> {val_json}</span>"
            )

        html_lines.append("</pre>")
        html_lines.append("</div>")

        # Panel B
        html_lines.append("<div class='panel'>")
        html_lines.append(f"<h2>{file_b_name}</h2>")
        html_lines.append("<pre>")

        # Only in B (red)
        for key, value in sorted(diff_result['only_in_b'].items()):
            html_lines.append(f"<span class='only-b'><span class='key'>{key}:</span> {json.dumps(value)}</span>")

        # Common (yellow)
        for key, values in sorted(diff_result['common'].items()):
            html_lines.append(f"<span class='common'><span class='key'>{key}:</span> {json.dumps(values['b'])}</span>")

        # Modified (orange) - show value from B
        for key, values in sorted(diff_result['modified'].items()):
            val_json = json.dumps(values['b'])
            html_lines.append(
                f"<span class='modified'><span class='key'>{key}:</span> {val_json}</span>"
            )

        html_lines.append("</pre>")
        html_lines.append("</div>")

        html_lines.append("</div>")
        html_lines.append("</body>")
        html_lines.append("</html>")

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(html_lines))
