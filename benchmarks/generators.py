"""
Test Data Generators

Generate JSON, HTML, and other test data of various sizes for benchmarking.
Ensures consistent test data across benchmark runs.

Author: Clarify Project
Version: 2.9.81
Date: 2025-12-21
"""

import json
import random
import string
from typing import Dict, Any, List


def generate_json_data(size_mb: float) -> dict:
    """
    Generate JSON dictionary with approximate size in MB.
    
    Creates realistic JSON structure with nested objects, arrays,
    and various data types to simulate real-world data.
    
    Args:
        size_mb: Target size in megabytes (approximate)
    
    Returns:
        Dictionary that serializes to ~size_mb MB of JSON
    
    Example:
        >>> data = generate_json_data(1.0)  # ~1MB
        >>> import json
        >>> size = len(json.dumps(data).encode('utf-8'))
        >>> 0.9 * 1024 * 1024 < size < 1.1 * 1024 * 1024
        True
    """
    target_bytes = int(size_mb * 1024 * 1024)
    
    # Estimate: each item ~200 bytes (with JSON overhead)
    num_items = target_bytes // 200
    
    data = {
        "metadata": {
            "version": "1.0",
            "generated": "2025-12-21",
            "size_mb": size_mb,
            "item_count": num_items
        },
        "items": []
    }
    
    for i in range(num_items):
        item = {
            "id": i,
            "name": f"Item_{i}_{_random_string(10)}",
            "description": _random_string(50),
            "value": random.randint(1, 10000),
            "price": round(random.uniform(10.0, 999.99), 2),
            "active": random.choice([True, False]),
            "tags": [_random_string(5) for _ in range(random.randint(1, 5))],
            "metadata": {
                "created": f"2025-12-{random.randint(1, 21):02d}",
                "updated": f"2025-12-21T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00Z",
                "author": f"user_{random.randint(1, 100)}"
            }
        }
        data["items"].append(item)
    
    return data


def generate_nested_json(depth: int, breadth: int) -> dict:
    """
    Generate deeply nested JSON structure for search benchmarks.
    
    Creates tree structure with specified depth and breadth to test
    recursive search algorithms.
    
    Args:
        depth: Maximum nesting level (e.g., 20 = 20 levels deep)
        breadth: Number of children at each level
    
    Returns:
        Deeply nested dictionary
    
    Example:
        >>> data = generate_nested_json(depth=3, breadth=2)
        >>> # Result: {"level_0": {"child_0": {...}, "child_1": {...}}}
    """
    def _build_level(current_depth: int) -> dict:
        if current_depth >= depth:
            return {
                "leaf": True,
                "value": _random_string(20),
                "depth": current_depth
            }
        
        node = {
            "level": current_depth,
            "value": f"node_{current_depth}_{_random_string(8)}",
            "data": {
                "count": random.randint(1, 100),
                "active": random.choice([True, False])
            }
        }
        
        # Add children
        for i in range(breadth):
            node[f"child_{i}"] = _build_level(current_depth + 1)
        
        return node
    
    return {
        "root": _build_level(0),
        "metadata": {
            "max_depth": depth,
            "breadth": breadth,
            "total_nodes": (breadth ** depth - 1) // (breadth - 1) if breadth > 1 else depth
        }
    }


def generate_html_content(size_mb: float) -> str:
    """
    Generate HTML content for text extractor benchmarks.
    
    Creates realistic HTML with various tags (div, span, p, h1-h6)
    to simulate web scraping scenarios.
    
    Args:
        size_mb: Target size in megabytes
    
    Returns:
        HTML string
    
    Example:
        >>> html = generate_html_content(0.5)  # 500KB
        >>> '<html>' in html and '</html>' in html
        True
    """
    target_bytes = int(size_mb * 1024 * 1024)
    
    # Estimate: each div ~150 bytes
    num_divs = target_bytes // 150
    
    html_parts = ['<!DOCTYPE html>\n<html>\n<head>\n<title>Benchmark Test</title>\n</head>\n<body>\n']
    
    for i in range(num_divs):
        tag = random.choice(['div', 'span', 'p', 'section', 'article'])
        class_name = f"class-{random.randint(1, 50)}"
        text = _random_string(random.randint(20, 80))
        
        html_parts.append(f'<{tag} class="{class_name}">{text}</{tag}>\n')
        
        # Add nested structure occasionally
        if i % 10 == 0:
            html_parts.append('<div class="nested">\n')
            for j in range(3):
                html_parts.append(f'  <p>{_random_string(30)}</p>\n')
            html_parts.append('</div>\n')
    
    html_parts.append('</body>\n</html>')
    
    return ''.join(html_parts)


def generate_jsx_content(num_components: int) -> str:
    """
    Generate JSX content for text extractor benchmarks.
    
    Creates React components with various props and nested structure.
    
    Args:
        num_components: Number of JSX components to generate
    
    Returns:
        JSX string
    
    Example:
        >>> jsx = generate_jsx_content(10)
        >>> 'function Component' in jsx
        True
    """
    jsx_parts = ['import React from "react";\n\n']
    
    for i in range(num_components):
        component_name = f"Component{i}"
        props_count = random.randint(2, 5)
        
        jsx_parts.append(f'function {component_name}(props) {{\n')
        jsx_parts.append('  return (\n')
        jsx_parts.append(f'    <div className="component-{i}">\n')
        jsx_parts.append(f'      <h2>{_random_string(15)}</h2>\n')
        
        for j in range(props_count):
            jsx_parts.append(f'      <p>{{props.prop{j}}}</p>\n')
        
        jsx_parts.append('    </div>\n')
        jsx_parts.append('  );\n')
        jsx_parts.append('}\n\n')
    
    jsx_parts.append(f'export default Component0;\n')
    
    return ''.join(jsx_parts)


def generate_array_with_duplicates(size: int, duplicate_ratio: float = 0.3) -> list:
    """
    Generate array with duplicates for deduplication benchmarks.
    
    Args:
        size: Number of items in array
        duplicate_ratio: Fraction of items that are duplicates (0.0-1.0)
    
    Returns:
        List with duplicates
    
    Example:
        >>> arr = generate_array_with_duplicates(100, 0.5)
        >>> len(arr) == 100
        True
    """
    unique_count = int(size * (1 - duplicate_ratio))
    
    # Generate unique items
    unique_items = [
        {
            "id": i,
            "value": _random_string(20),
            "timestamp": f"2025-12-{random.randint(1, 21):02d}"
        }
        for i in range(unique_count)
    ]
    
    # Add duplicates by repeating random items
    result = unique_items.copy()
    duplicates_needed = size - unique_count
    
    for _ in range(duplicates_needed):
        result.append(random.choice(unique_items))
    
    # Shuffle to mix duplicates
    random.shuffle(result)
    
    return result


def _random_string(length: int) -> str:
    """Generate random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_jsx_content(size_kb: int) -> str:
    """
    Generate JSX content for Advanced Extractor benchmarks (v2.9.115).
    
    Creates realistic React/JSX components with attributes and nested structure
    to benchmark the Advanced Extractor tool.
    
    Args:
        size_kb: Target size in kilobytes
    
    Returns:
        JSX code string
    
    Example:
        >>> jsx = generate_jsx_content(10)
        >>> 'label=' in jsx
        True
    """
    target_bytes = size_kb * 1024
    jsx_parts = []
    
    # Header
    jsx_parts.append("import React from 'react';\n\n")
    
    # Generate components until we reach target size
    component_count = 0
    current_size = sum(len(part.encode('utf-8')) for part in jsx_parts)
    
    while current_size < target_bytes:
        # Generate component with random attributes
        jsx_parts.append(f"function Component{component_count}() {{\n")
        jsx_parts.append("  return (\n")
        jsx_parts.append("    <div>\n")
        
        # Add nested components with label attributes
        for i in range(random.randint(3, 8)):
            label = f"Label {component_count}.{i} - {_random_string(15)}"
            title = f"Title {_random_string(10)}"
            jsx_parts.append(f'      <Button label="{label}" title="{title}">\n')
            jsx_parts.append(f'        <Icon label="icon_{i}" />\n')
            jsx_parts.append(f'        <Text>{_random_string(20)}</Text>\n')
            jsx_parts.append('      </Button>\n')
        
        jsx_parts.append("    </div>\n")
        jsx_parts.append("  );\n")
        jsx_parts.append("}\n\n")
        
        component_count += 1
        current_size = sum(len(part.encode('utf-8')) for part in jsx_parts)
    
    jsx_parts.append(f"export default Component0;\n")
    
    return ''.join(jsx_parts)


# Seed for reproducibility
random.seed(42)
