"""
CLI interface for code-edit tool.
"""
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from code_edit.core.processor import CodeProcessor
from code_edit.core.diff import create_diff_view

console = Console()

def validate_file(ctx, param, value):
    """Validate that the file exists and is readable."""
    if value is None:
        return None
    try:
        path = Path(value)
        if not path.is_file():
            raise click.BadParameter(f"File {value} does not exist")
        return path
    except Exception as e:
        raise click.BadParameter(str(e))

@click.command()
@click.option('--prompt', '-p', help='Natural language description of desired changes')
@click.option('--prompt-file', '-P', type=click.Path(exists=True), help='File containing change description')
@click.option('--file', '-f', callback=validate_file, required=True, help='Target code file to modify')
@click.option('--output', '-o', type=click.Path(), help='Output file (defaults to modifying input file)')
@click.option('--preview/--no-preview', default=False, help='Show changes without applying them')
def cli(prompt: Optional[str], prompt_file: Optional[str], file: Path, 
        output: Optional[str], preview: bool):
    """AI-powered code editing tool."""
    try:
        # Get prompt from file if specified
        if prompt_file and not prompt:
            with open(prompt_file) as f:
                prompt = f.read().strip()
        
        if not prompt:
            raise click.UsageError("Either --prompt or --prompt-file must be specified")

        # Initialize processor
        processor = CodeProcessor()
        
        # Show model information
        info = processor.get_model_info()
        console.print(f"[cyan]Using model:[/cyan] [green]{info.get('model', 'Unknown')}[/green]")
        console.print(f"[cyan]       File:[/cyan] [green]{file}[/green]")
        
        # Read input file
        with open(file) as f:
            original_code = f.read()

        # Process the code with progress tracking
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            task = progress.add_task("Processing code...", total=None)
            modified_code = processor.process(original_code, prompt)
            progress.update(task, completed=100)

        # Show diff if preview mode or different output file
        if preview or output:
            diff = create_diff_view(original_code, modified_code)
            console.print(diff)
            
            if preview:
                return

        # Write output
        output_file = Path(output) if output else file
        with open(output_file, 'w') as f:
            f.write(modified_code)
        
        console.print(f"[green]Successfully wrote changes to {output_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main() 