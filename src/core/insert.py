"""Text insertion at specific lines with multiple modes."""


# pylint: disable=too-few-public-methods  # Constants container class
class InsertMode:
    """Text insertion modes for line operations."""
    LEFT = "Insert left of line"
    RIGHT = "Insert right of line"
    REPLACE = "Replace line content"
    INSERT_ABOVE = "Push line down and insert above"
    INSERT_BELOW = "Insert on next line (push rest)"


def insert_at_line(content: str, line_no: int, text: str, mode: str) -> str:
    """
    Insert/modify 'text' at 1-based 'line_no' following 'mode'.
    """
    lines = content.splitlines(keepends=False)
    idx = max(0, min(len(lines), line_no - 1))

    if mode == InsertMode.LEFT:
        if idx >= len(lines):
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = text + lines[idx]

    elif mode == InsertMode.RIGHT:
        if idx >= len(lines):
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = lines[idx] + text

    elif mode == InsertMode.REPLACE:
        if idx >= len(lines):
            while len(lines) < idx:
                lines.append("")
            lines.append(text)
        else:
            lines[idx] = text

    elif mode == InsertMode.INSERT_ABOVE:
        lines.insert(idx, text)

    elif mode == InsertMode.INSERT_BELOW:
        lines.insert(min(idx + 1, len(lines)), text)

    else:
        raise ValueError(f"Unknown insert mode: {mode}")

    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
