"""
Diff generation functionality.
"""
import difflib
import re
from typing import List, Tuple, Optional

from rich.syntax import Syntax
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich import box

def highlight_word_diff(old_text: str, new_text: str) -> Text:
    """
    Highlight word-level differences between two texts.
    
    Args:
        old_text: The original text
        new_text: The modified text
        
    Returns:
        A rich Text object with highlighted word differences
    """
    result = Text()
    matcher = difflib.SequenceMatcher(None, old_text, new_text)
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            result.append(old_text[i1:i2])
        elif op == 'delete':
            # Use bold red text instead of white on red background
            result.append(old_text[i1:i2], style="bold red")
        elif op == 'insert':
            # Use bold green text instead of white on green background
            result.append(new_text[j1:j2], style="bold green")
        elif op == 'replace':
            result.append(old_text[i1:i2], style="bold red")
            result.append(" → ", style="bold")
            result.append(new_text[j1:j2], style="bold green")
            
    return result

def create_diff_view(original: str, modified: str, max_height: Optional[int] = None) -> Table:
    """
    Create a rich diff view comparing original and modified code.
    
    Args:
        original: Original code content
        modified: Modified code content
        max_height: Maximum height for the table (None means no limit)
        
    Returns:
        A rich Table object showing the diff
    """
    # Create a unified diff
    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile='Original',
        tofile='Modified',
        lineterm=''
    ))

    # Create a table for the diff with auto-adjustment for width
    # The height will be adjusted when the table is printed by the console
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE, expand=True)
    table.add_column("Line", style="dim", width=10, no_wrap=True)
    table.add_column("Changes", style="none", ratio=1)

    # Check if there are any differences
    if not diff:
        table.add_row("", Panel(Text("No differences found", style="italic")))
        return table

    # Process the diff lines
    line_num_original = 0
    line_num_modified = 0
    hunk_pattern = re.compile(r'^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@')
    
    # Store matched line pairs for word diff
    removed_lines = {}
    added_lines = {}
    last_removed_line = None
    
    # First pass: collect added and removed lines
    temp_line_original = 0
    temp_line_modified = 0
    
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            continue
            
        if line.startswith('@@'):
            match = hunk_pattern.match(line)
            if match:
                temp_line_original = int(match.group(1)) - 1
                temp_line_modified = int(match.group(3)) - 1
            continue
            
        if line.startswith('+'):
            temp_line_modified += 1
            added_lines[temp_line_modified] = line[1:]
            if last_removed_line is not None:
                # Try to match with the previous removed line
                removed_lines[last_removed_line] = (temp_line_modified, removed_lines.get(last_removed_line, (None, None))[1])
                last_removed_line = None
        elif line.startswith('-'):
            temp_line_original += 1
            last_removed_line = temp_line_original
            removed_lines[temp_line_original] = (None, line[1:])
        else:
            temp_line_original += 1
            temp_line_modified += 1
            last_removed_line = None
    
    # Second pass: create the diff view
    line_num_original = 0
    line_num_modified = 0
    
    for line in diff:
        if line.startswith('---') or line.startswith('+++'):
            continue
            
        if line.startswith('@@'):
            match = hunk_pattern.match(line)
            if match:
                line_num_original = int(match.group(1)) - 1
                line_num_modified = int(match.group(3)) - 1
            continue
            
        if line.startswith('+'):
            line_num_modified += 1
            
            # Check if this added line has a matching removed line
            matched = False
            for orig_line, (mod_line, orig_content) in removed_lines.items():
                if mod_line == line_num_modified and orig_content is not None:
                    # Found a matching line, show word diff
                    matched = True
                    word_diff = highlight_word_diff(orig_content, line[1:])
                    table.add_row(f"+{line_num_modified}", word_diff)
                    break
            
            if not matched:
                # No match, show as a completely new line
                # Use bold green text instead of white on green background
                table.add_row(
                    f"+{line_num_modified}",
                    Text(line[1:], style="bold green")
                )
                
        elif line.startswith('-'):
            line_num_original += 1
            
            # Check if this has a matching added line
            if line_num_original in removed_lines and removed_lines[line_num_original][0] is not None:
                # This will be shown with word diff when we process the matching added line
                continue
            else:
                # No match, show as a completely removed line
                # Use bold red text instead of white on red background
                table.add_row(
                    f"-{line_num_original}",
                    Text(line[1:], style="bold red")
                )
                
        else:
            line_num_original += 1
            line_num_modified += 1
            table.add_row(
                f"{line_num_original}",
                Syntax(line[1:], "python", theme="monokai")
            )

    return table