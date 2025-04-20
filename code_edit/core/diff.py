"""
Diff generation functionality.
"""
import difflib
from typing import List

from rich.syntax import Syntax
from rich.console import Console
from rich.table import Table

def create_diff_view(original: str, modified: str) -> Table:
    """
    Create a rich diff view comparing original and modified code.
    
    Args:
        original: Original code content
        modified: Modified code content
        
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

    # Create a table for the diff
    table = Table(show_header=True, header_style="bold")
    table.add_column("Line", style="dim")
    table.add_column("Changes", style="none")

    # Process the diff lines
    line_num = 0
    for line in diff:
        # Skip the header lines
        if line.startswith('---') or line.startswith('+++'):
            continue
        
        # Handle line number indicators
        if line.startswith('@@'):
            continue
            
        # Process the actual diff lines
        if line.startswith('+'):
            table.add_row(
                str(line_num),
                Syntax(line[1:], "python", theme="monokai", background_color="green")
            )
        elif line.startswith('-'):
            table.add_row(
                str(line_num),
                Syntax(line[1:], "python", theme="monokai", background_color="red")
            )
        else:
            table.add_row(
                str(line_num),
                Syntax(line[1:], "python", theme="monokai")
            )
        line_num += 1

    return table 