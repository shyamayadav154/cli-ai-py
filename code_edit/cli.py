"""
CLI interface for code-edit tool.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress
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

# Define common options as decorators
def common_options(f):
    f = click.option('--prompt', '-p', help='Natural language description of desired changes')(f)
    f = click.option('--prompt-file', '-P', type=click.Path(exists=True), help='File containing change description')(f)
    f = click.option('--file', '-f', callback=validate_file, required=True, help='Target code file to modify')(f)
    f = click.option('--output', '-o', type=click.Path(), help='Output file (defaults to modifying input file)')(f)
    f = click.option('--preview/--no-preview', default=False, help='Show changes without applying them')(f)
    return f

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """AI-powered code editing tool.
    
    Commands:
      edit        Edit code using AI (default command)
      model-info  Show information about the current AI model
    
    Run 'code-edit COMMAND --help' for help on specific commands.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(edit)

@cli.command()
@common_options
def edit(prompt: Optional[str], prompt_file: Optional[str], file: Path, 
         output: Optional[str], preview: bool):
    """Edit code using AI."""
    try:
        # Get prompt from file if specified
        if prompt_file and not prompt:
            with open(prompt_file) as f:
                prompt = f.read().strip()
        
        if not prompt:
            raise click.UsageError("Either --prompt or --prompt-file must be specified")

        # Initialize processor
        processor = CodeProcessor()
        
        # Read input file
        with open(file) as f:
            original_code = f.read()

        # Process the code
        with Progress() as progress:
            task = progress.add_task("Processing...", total=100)
            progress.update(task, advance=50)
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

@cli.command()
def model_info():
    """Show information about the current AI model."""
    try:
        processor = CodeProcessor()
        info = processor.get_model_info()
        
        # Create a pretty table
        table = Table(title="AI Model Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            table.add_row(key.title(), value)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main() 