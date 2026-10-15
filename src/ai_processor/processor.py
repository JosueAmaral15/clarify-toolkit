"""
AI Processor Module

Core file processing logic for AI-powered batch operations.
"""
# pylint: disable=broad-exception-caught  # File processing robustness

import os
import re
from typing import List, Optional, Callable
from .template_engine import render_prompt, has_templates


def extract_between_markers(
    text: str,
    start_marker: str,
    end_marker: str,
    start_regex: bool = False,
    start_case_sensitive: bool = False,
    end_regex: bool = False,
    end_case_sensitive: bool = False,
    include_markers: bool = False,
    match_all: bool = True
) -> str:
    """
    Extract content between start and end markers.

    Args:
        text: Input text
        start_marker: Start marker (plain text or regex)
        end_marker: End marker (plain text or regex)
        start_regex: Treat start_marker as regex
        start_case_sensitive: Case sensitive start matching
        end_regex: Treat end_marker as regex
        end_case_sensitive: Case sensitive end matching
        include_markers: Include markers in extracted text
        match_all: Extract all matches (True) or only first (False)

    Returns:
        Extracted text
    """
    if not (start_marker and end_marker):
        return text

    # Build start pattern
    if start_regex:
        start_pat = start_marker
    else:
        start_pat = re.escape(start_marker)

    # Build end pattern
    if end_regex:
        end_pat = end_marker
    else:
        end_pat = re.escape(end_marker)

    # Compile with independent case flags
    flags_start = 0 if start_case_sensitive else re.IGNORECASE
    flags_end = 0 if end_case_sensitive else re.IGNORECASE

    start_re = re.compile(start_pat, flags_start)
    end_re = re.compile(end_pat, flags_end)

    out = []
    i = 0

    # Non-overlapping segment finder
    while i <= len(text):
        m_start = start_re.search(text, i)
        if not m_start:
            break
        m_end = end_re.search(text, m_start.end())
        if not m_end:
            break

        if include_markers:
            seg = text[m_start.start(): m_end.end()]
        else:
            seg = text[m_start.end(): m_end.start()]

        out.append(seg)
        i = m_end.end()
        if not match_all:
            break

    return "".join(out) if out else text


def read_file_safe(file_path: str, max_bytes: Optional[int] = None) -> str:
    """
    Safely read file content with optional byte limit.

    Args:
        file_path: Path to file
        max_bytes: Maximum bytes to read (None = no limit)

    Returns:
        File content as string
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read() if max_bytes is None else f.read(max_bytes)

        # Try UTF-8 first, fallback to latin-1
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1', errors='replace')
    except Exception as e:
        return f"<<ERROR reading {file_path}: {str(e)}>>"


def list_files_recursive(
    directory: str,
    extensions: List[str],
    *,
    checkpoint: Optional[Callable[[], bool]] = None,
    max_files: Optional[int] = None,
) -> List[str]:
    """
    List all files in directory recursively, optionally filtered by extensions.

    Args:
        directory: Root directory path
        extensions: List of extensions to filter (e.g., ['.txt', '.py'])
                   Empty list = all files

    Returns:
        List of absolute file paths
    """
    files = []
    for root, _, filenames in os.walk(directory):
        if checkpoint is not None and not checkpoint():
            break
        for filename in filenames:
            if checkpoint is not None and not checkpoint():
                return files
            if not extensions or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
                if max_files is not None and len(files) > max_files:
                    raise ValueError(
                        f"File discovery exceeds the {max_files}-file remaining safety limit"
                    )
    return files


def strip_code_fences(text: str) -> str:
    """
    Remove markdown code fences from AI responses.

    Examples:
        ```python\ncode\n``` -> code
        ```json\n{...}\n``` -> {...}

    Args:
        text: Input text with potential code fences

    Returns:
        Text with code fences removed
    """
    # Remove opening fence with optional language
    text = re.sub(r'^```[a-z]*\n', '', text, flags=re.MULTILINE)
    # Remove closing fence
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()


def process_file(
    file_path: str,
    prompt: str,
    client,
    max_bytes: Optional[int],
    progress_callback: Optional[Callable[[str], None]] = None,
    scope_filter_enabled: bool = False,
    scope_start: str = "",
    scope_end: str = "",
    scope_start_regex: bool = False,
    scope_start_case: bool = False,
    scope_end_regex: bool = False,
    scope_end_case: bool = False,
    template_enabled: bool = False,
    file_index: int = 0,
    total_files: int = 1
) -> str:
    """
    Process a single file with AI.

    Args:
        file_path: Path to file
        prompt: User prompt/instruction
        client: AI client (OpenAIClient or GeminiClient)
        max_bytes: Max bytes to read from file
        progress_callback: Optional callback for progress updates
        scope_filter_enabled: Enable scope filtering
        scope_start: Start marker
        scope_end: End marker
        scope_start_regex: Treat start as regex
        scope_start_case: Case sensitive start
        scope_end_regex: Treat end as regex
        scope_end_case: Case sensitive end
        template_enabled: Enable template variable substitution ({{count}}, {{filename}}, etc.)
        file_index: Current file index (0-based) for templates
        total_files: Total number of files for templates

    Returns:
        AI response
    """
    # Apply template rendering if enabled
    if template_enabled and has_templates(prompt):
        prompt = render_prompt(prompt, file_index, total_files, file_path)

    if progress_callback:
        progress_callback(f"Reading {os.path.basename(file_path)}...")

    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    if (
        os.path.splitext(file_path)[1].lower() in image_extensions
        and hasattr(client, "chat_with_image")
    ):
        image_prompt = f"{prompt}\n\n# Image file: {file_path}"
        return client.chat_with_image(
            "You are a helpful assistant. Analyze the provided image and respond "
            "according to the user's instructions.",
            image_prompt,
            file_path,
            max_bytes=max_bytes,
        )

    content = read_file_safe(file_path, max_bytes)

    # Apply scope filter if enabled
    if scope_filter_enabled and scope_start and scope_end:
        content = extract_between_markers(
            content,
            scope_start,
            scope_end,
            start_regex=scope_start_regex,
            start_case_sensitive=scope_start_case,
            end_regex=scope_end_regex,
            end_case_sensitive=scope_end_case,
            include_markers=False,
            match_all=True
        )

    user_prompt = f"{prompt}\n\n# File: {file_path}\n```\n{content}\n```"

    if progress_callback:
        progress_callback(f"Sending {os.path.basename(file_path)} to AI...")

    system_prompt = (
        "You are a helpful assistant. Analyze the provided file and respond "
        "according to the user's instructions."
    )
    response = client.chat(system_prompt, user_prompt)

    return strip_code_fences(response.strip())


def process_multiple_files(
    file_paths: List[str],
    prompt: str,
    client,
    max_bytes: Optional[int],
    line_by_line: bool,
    progress_callback: Optional[Callable[[str], None]] = None,
    interrupt_check: Optional[Callable[[], bool]] = None,
    scope_filter_enabled: bool = False,
    scope_start: str = "",
    scope_end: str = "",
    scope_start_regex: bool = False,
    scope_start_case: bool = False,
    scope_end_regex: bool = False,
    scope_end_case: bool = False,
    template_enabled: bool = False
) -> List[str]:
    """
    Process multiple files with AI.

    Args:
        file_paths: List of file paths to process
        prompt: User prompt/instruction (or list of prompts for line-by-line)
        client: AI client
        max_bytes: Max bytes per file
        line_by_line: If True, use prompt lines cyclically for each file
        progress_callback: Optional callback for progress updates
        interrupt_check: Optional callback to check if processing should stop
        scope_filter_enabled: Enable scope filtering
        scope_start: Start marker
        scope_end: End marker
        scope_start_regex: Treat start as regex
        scope_start_case: Case sensitive start
        scope_end_regex: Treat end as regex
        scope_end_case: Case sensitive end
        template_enabled: Enable template variable substitution ({{count}}, {{filename}}, etc.)

    Returns:
        List of AI responses (one per file)
    """
    responses = []
    prompt_lines = prompt.splitlines() if line_by_line else []
    total_files = len(file_paths)

    for i, file_path in enumerate(file_paths):
        # Check for interrupt
        if interrupt_check and interrupt_check():
            if progress_callback:
                progress_callback("⚠️ Processing interrupted by user")
            break

        # Select prompt
        if line_by_line and prompt_lines:
            current_prompt = prompt_lines[i % len(prompt_lines)]
        else:
            current_prompt = prompt

        # Process file
        if progress_callback:
            progress_callback(f"[{i+1}/{len(file_paths)}] Processing {os.path.basename(file_path)}...")

        response = process_file(
            file_path, current_prompt, client, max_bytes, progress_callback,
            scope_filter_enabled, scope_start, scope_end,
            scope_start_regex, scope_start_case,
            scope_end_regex, scope_end_case,
            template_enabled, i, total_files
        )
        responses.append(response)

        if progress_callback:
            progress_callback(f"✓ Completed {os.path.basename(file_path)}")

    return responses


def save_results(
    results: List[str],
    output_path: str,
    mode: str = 'write'
) -> None:
    """
    Save processing results to file.

    Args:
        results: List of AI responses
        output_path: Output file path
        mode: 'write' (overwrite) or 'append'
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    mode_flag = 'a' if mode == 'append' else 'w'
    with open(output_path, mode_flag, encoding='utf-8') as f:
        for i, result in enumerate(results, 1):
            f.write(f"=== Result {i} ===\n")
            f.write(result)
            f.write("\n\n")
