#!/usr/bin/env python3
"""
Changelog Automation Script - Sprint v2.9.59

Generates changelog entries from git commits using Conventional Commits format.
Adds new entries to existing CHANGELOG.md under [Unreleased] section.

Usage:
    python scripts/generate_changelog.py
    python scripts/generate_changelog.py --since="2025-12-01"
    python scripts/generate_changelog.py --output=CHANGELOG_NEW.md

Supported commit types:
    - feat: New features (✨)
    - fix: Bug fixes (🐛)
    - docs: Documentation (📝)
    - refactor: Code refactoring (♻️)
    - test: Tests (🧪)
    - chore: Maintenance (🔧)
    - perf: Performance improvements (⚡)
    - style: Code style changes (💄)
"""

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


# Emoji mapping for commit types
COMMIT_EMOJIS = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📝",
    "refactor": "♻️",
    "test": "🧪",
    "chore": "🔧",
    "perf": "⚡",
    "style": "💄",
}

# Section titles for commit types
COMMIT_SECTIONS = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "refactor": "Refactoring",
    "test": "Testing",
    "chore": "Maintenance",
    "perf": "Performance",
    "style": "Code Style",
}


def parse_commit_message(message: str) -> Tuple[str, str, str, str]:
    """
    Parse conventional commit message.
    
    Format: type(scope): description
    
    Args:
        message: Full commit message
        
    Returns:
        Tuple of (type, scope, description, body)
    """
    # Match conventional commit format: type(scope): description
    pattern = r"^(\w+)(?:\(([^)]+)\))?: (.+)$"
    match = re.match(pattern, message.split("\n")[0])
    
    if match:
        commit_type, scope, description = match.groups()
        # Extract body (everything after first line)
        lines = message.split("\n")
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        return commit_type, scope or "", description, body
    
    # If not conventional format, treat as "chore"
    return "chore", "", message.split("\n")[0], ""


def get_commits_since(since_ref: str = None) -> List[Dict[str, str]]:
    """
    Get git commits since a reference point.
    
    Args:
        since_ref: Git reference (commit hash, tag, date). If None, gets last 20 commits.
        
    Returns:
        List of commit dictionaries with hash, message, author, date
    """
    # Build git log command
    cmd = ["git", "log", "--format=%H%n%s%n%b%n%an%n%ai%n---END---"]
    
    if since_ref:
        cmd.append(f"{since_ref}..HEAD")
    else:
        cmd.append("-20")  # Last 20 commits by default
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e}")
        return []
    
    # Parse output
    commits = []
    commit_texts = result.stdout.split("---END---\n")
    
    for commit_text in commit_texts:
        if not commit_text.strip():
            continue
            
        lines = commit_text.strip().split("\n")
        if len(lines) < 5:
            continue
        
        commit_hash = lines[0]
        subject = lines[1]
        
        # Find body (between subject and author)
        body_lines = []
        author_idx = -2
        for i, line in enumerate(lines[2:], start=2):
            if i == len(lines) - 2:  # Author line
                author_idx = i
                break
            body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        author = lines[author_idx] if author_idx > 0 else "Unknown"
        date = lines[author_idx + 1] if author_idx > 0 else ""
        
        commits.append({
            "hash": commit_hash[:7],  # Short hash
            "subject": subject,
            "body": body,
            "author": author,
            "date": date,
        })
    
    return commits


def get_last_changelog_commit() -> str:
    """
    Get the last commit that modified CHANGELOG.md.
    
    Returns:
        Commit hash or empty string if not found
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "CHANGELOG.md"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def group_commits_by_type(commits: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
    """
    Group commits by their type (feat, fix, docs, etc.).
    
    Args:
        commits: List of commit dictionaries
        
    Returns:
        Dictionary with type as key and list of commits as value
    """
    grouped = {}
    
    for commit in commits:
        commit_type, scope, description, body = parse_commit_message(
            commit["subject"] + "\n" + commit["body"]
        )
        
        if commit_type not in grouped:
            grouped[commit_type] = []
        
        grouped[commit_type].append({
            "hash": commit["hash"],
            "scope": scope,
            "description": description,
            "body": body,
            "author": commit["author"],
            "date": commit["date"],
        })
    
    return grouped


def format_changelog_entry(commit: Dict[str, str], include_body: bool = True) -> str:
    """
    Format a single commit as a changelog entry.
    
    Args:
        commit: Commit dictionary
        include_body: Whether to include commit body
        
    Returns:
        Formatted markdown string
    """
    scope = f"**{commit['scope']}**: " if commit["scope"] else ""
    entry = f"- {scope}{commit['description']} ({commit['hash']})"
    
    if include_body and commit["body"]:
        # Format body as bullet points (indented)
        body_lines = commit["body"].split("\n")
        for line in body_lines:
            line = line.strip()
            if line and not line.startswith("-") and not line.startswith("*"):
                entry += f"\n  * {line}"
            elif line:
                entry += f"\n  {line}"
    
    return entry


def generate_changelog_section(
    grouped_commits: Dict[str, List[Dict]], 
    version: str = "Unreleased"
) -> str:
    """
    Generate changelog section with all commits grouped by type.
    
    Args:
        grouped_commits: Commits grouped by type
        version: Version string (default: "Unreleased")
        
    Returns:
        Formatted markdown section
    """
    today = datetime.now().strftime("%Y-%m-%d")
    output = [f"## [{version}] - {today}\n"]
    
    # Sort by priority: feat, fix, docs, refactor, test, perf, style, chore
    priority = ["feat", "fix", "docs", "refactor", "test", "perf", "style", "chore"]
    sorted_types = sorted(
        grouped_commits.keys(),
        key=lambda x: priority.index(x) if x in priority else 999
    )
    
    for commit_type in sorted_types:
        commits = grouped_commits[commit_type]
        if not commits:
            continue
        
        emoji = COMMIT_EMOJIS.get(commit_type, "📌")
        section_title = COMMIT_SECTIONS.get(commit_type, commit_type.capitalize())
        
        output.append(f"### {emoji} {section_title}\n")
        
        for commit in commits:
            entry = format_changelog_entry(commit, include_body=True)
            output.append(entry)
        
        output.append("")  # Blank line after section
    
    return "\n".join(output)


def insert_changelog_section(
    changelog_path: Path, 
    new_section: str
) -> None:
    """
    Insert new changelog section at the top of existing CHANGELOG.md.
    
    Args:
        changelog_path: Path to CHANGELOG.md
        new_section: New section content to insert
    """
    if not changelog_path.exists():
        # Create new CHANGELOG.md
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write("# Changelog - Clarify Project\n\n")
            f.write(new_section)
        print(f"✅ Created new {changelog_path}")
        return
    
    # Read existing content
    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find insertion point (after header, before first version)
    lines = content.split("\n")
    insert_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith("# Changelog"):
            insert_idx = i + 1
            # Skip empty lines after header
            while insert_idx < len(lines) and not lines[insert_idx].strip():
                insert_idx += 1
            break
    
    # Insert new section
    lines.insert(insert_idx, new_section)
    lines.insert(insert_idx + 1, "")  # Blank line separator
    
    # Write back
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ Updated {changelog_path} with new section")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelog from git commits"
    )
    parser.add_argument(
        "--since",
        help="Generate changelog since this reference (commit hash, tag, or date)",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: CHANGELOG.md)",
        default="CHANGELOG.md",
    )
    parser.add_argument(
        "--version",
        help="Version string (default: Unreleased)",
        default="Unreleased",
    )
    parser.add_argument(
        "--auto-since",
        help="Automatically use last CHANGELOG.md commit as reference",
        action="store_true",
    )
    
    args = parser.parse_args()
    
    # Determine since reference
    since_ref = args.since
    if args.auto_since and not since_ref:
        since_ref = get_last_changelog_commit()
        if since_ref:
            print(f"📍 Using last CHANGELOG.md commit as reference: {since_ref[:7]}")
        else:
            print("⚠️  No previous CHANGELOG.md commits found, using last 20 commits")
    
    # Get commits
    print(f"🔍 Fetching commits since {since_ref or 'last 20 commits'}...")
    commits = get_commits_since(since_ref)
    
    if not commits:
        print("❌ No commits found")
        return
    
    print(f"📝 Found {len(commits)} commits")
    
    # Group by type
    grouped = group_commits_by_type(commits)
    
    # Generate section
    new_section = generate_changelog_section(grouped, args.version)
    
    # Output path
    output_path = Path(__file__).parent.parent / args.output
    
    # Insert or create
    insert_changelog_section(output_path, new_section)
    
    print(f"\n✨ Changelog generation complete!")
    print(f"   Version: [{args.version}]")
    print(f"   Commits: {len(commits)}")
    print(f"   Types: {', '.join(grouped.keys())}")


if __name__ == "__main__":
    main()
