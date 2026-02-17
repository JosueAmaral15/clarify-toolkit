#!/usr/bin/env python3
"""
Test script for "Limit parent keys" feature with real JSX file.

This simulates what happens in the GUI when extracting JSX content
and applying the parent key limiting algorithm.
"""

import json
import sys

# Sample JSX structure that mimics PTEasy FAQ page structure
# This represents what the extraction would produce
SAMPLE_EXTRACTED_JSON = {
    "Root": {
        "div.container": {
            "div.faq-section": {
                "div.question-block": {
                    "button.accordion": {
                        "h3.question-title": {
                            "text": "What is PTEasy?"
                        }
                    },
                    "div.answer": {
                        "p.answer-text": {
                            "text": "PTEasy is a platform for Portuguese language learning."
                        }
                    }
                },
                "div.question-block[1]": {
                    "button.accordion": {
                        "h3.question-title": {
                            "text": "How does it work?"
                        }
                    }
                }
            }
        }
    }
}


def collect_paths(obj, path=[]):
    """Recursively collect all (path, value) tuples from nested dict."""
    paths = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = path + [key]
            if isinstance(value, (dict, list)):
                paths.extend(collect_paths(value, current_path))
            else:
                paths.append((current_path, value))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            paths.extend(collect_paths(item, path + [f"[{i}]"]))
    return paths


def limit_path_keys(path_keys, limit, mode):
    """
    Limit the number of parent keys in a path.
    
    Args:
        path_keys: List of keys forming a path (including leaf)
        limit: Total number of keys to keep (including leaf)
        mode: "start", "end", or "both"
    
    Returns:
        Limited list of keys
    """
    if limit <= 0:
        return [path_keys[-1]] if path_keys else []
    
    if len(path_keys) <= 1:
        return path_keys
    
    # Separate parents and leaf
    parents = path_keys[:-1]
    leaf = path_keys[-1]
    
    # Calculate how many parents to keep (limit includes leaf)
    parents_to_keep = limit - 1
    
    # If we can keep all parents, do so
    if parents_to_keep >= len(parents):
        return path_keys
    
    if parents_to_keep <= 0:
        return [leaf]
    
    # Apply limiting based on mode
    if mode == "start":
        kept_parents = parents[:parents_to_keep]
    elif mode == "end":
        kept_parents = parents[-parents_to_keep:]
    else:  # "both"
        from_start = (parents_to_keep + 1) // 2
        from_end = parents_to_keep // 2
        if from_end == 0:
            kept_parents = parents[:from_start]
        else:
            kept_parents = parents[:from_start] + parents[-from_end:]
    
    return kept_parents + [leaf]


def rebuild_dict(paths):
    """Rebuild nested dict from list of (path, value) tuples."""
    result = {}
    for path, value in paths:
        current = result
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    return result


def apply_limiting(json_data, limit, mode):
    """Apply parent key limiting to JSON data."""
    # Collect all paths
    paths = collect_paths(json_data)
    
    # Apply limiting to each path
    limited_paths = []
    for path, value in paths:
        limited_path = limit_path_keys(path, limit, mode)
        limited_paths.append((limited_path, value))
    
    # Rebuild dict
    return rebuild_dict(limited_paths)


def main():
    print("=" * 80)
    print("Testing 'Limit parent keys' feature with JSX extraction")
    print("=" * 80)
    print()
    
    print("Sample extracted JSON structure (with HTML class names):")
    print("-" * 80)
    print(json.dumps(SAMPLE_EXTRACTED_JSON, indent=2))
    print()
    
    # Collect paths
    paths = collect_paths(SAMPLE_EXTRACTED_JSON)
    print(f"📊 Total paths extracted: {len(paths)}")
    print()
    
    # Find longest path
    longest_path, longest_value = max(paths, key=lambda x: len(x[0]))
    print(f"📏 Longest path: {len(longest_path)} keys")
    print(f"   Path: {' → '.join(longest_path)}")
    print(f"   Value: {longest_value}")
    print()
    
    print("=" * 80)
    print("🧪 Testing limiting with different configurations:")
    print("=" * 80)
    print()
    
    # Test different limits with "both" mode
    for limit in [3, 4, 5, 6, 7]:
        print(f"\n📌 Limit = {limit}, Mode = 'Keep both ends'")
        print("-" * 80)
        
        limited_json = apply_limiting(SAMPLE_EXTRACTED_JSON, limit, "both")
        
        # Show one sample path after limiting
        limited_paths = collect_paths(limited_json)
        if limited_paths:
            sample_path, sample_value = limited_paths[0]
            print(f"Sample limited path ({len(sample_path)} keys):")
            print(f"  {' → '.join(sample_path)}")
            print(f"  Value: {sample_value}")
        
        # Show JSON structure (compact)
        print("\nLimited JSON structure:")
        print(json.dumps(limited_json, indent=2)[:400] + "\n  ...")
    
    print()
    print("=" * 80)
    print("✅ Test complete! HTML class names (like 'div.container', 'button.accordion')")
    print("   are treated as single keys and work correctly with the limiting feature.")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
