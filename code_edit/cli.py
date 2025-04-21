"""
CLI interface for code-edit tool.
"""
import os
import sys
import time
from pathlib import Path
from typing import Optional, List
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

def validate_files(ctx, param, value):
    """Validate that all files exist and are readable."""
    if not value:
        return []
    
    valid_files = []
    for file_path in value:
        try:
            path = Path(file_path)
            if not path.is_file():
                raise click.BadParameter(f"File {file_path} does not exist")
            valid_files.append(path)
        except Exception as e:
            raise click.BadParameter(str(e))
    
    return valid_files

@click.command()
@click.option('--prompt', '-p', help='Natural language description of desired changes')
@click.option('--prompt-file', '-P', type=click.Path(exists=True), help='File containing change description')
@click.argument('files', nargs=-1, callback=validate_files, required=False)
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory (defaults to modifying input files)')
@click.option('--preview/--no-preview', default=False, help='Show changes without applying them')
@click.option('--delay', '-d', type=int, default=0, help='Delay in seconds between processing files')
def cli(prompt: Optional[str], prompt_file: Optional[str], files: List[Path], 
        output_dir: Optional[str], preview: bool, delay: int):
    """AI-powered code editing tool. Can receive filenames from arguments or stdin."""
    try:
        # Get prompt from file if specified
        if prompt_file and not prompt:
            with open(prompt_file) as f:
                prompt = f.read().strip()
        
        if not prompt:
            raise click.UsageError("Either --prompt or --prompt-file must be specified")
        
        # Get files from stdin if no files are provided as arguments
        file_paths = list(files)
        if not file_paths and not sys.stdin.isatty():
            # Read filenames from stdin (one per line)
            for line in sys.stdin:
                file_path = line.strip()
                if file_path:
                    path = Path(file_path)
                    if path.is_file():
                        file_paths.append(path)
                    else:
                        console.print(f"[yellow]Warning: File {file_path} does not exist or is not readable, skipping[/yellow]")
        
        if not file_paths:
            raise click.UsageError("No valid files provided. Provide files as arguments or pipe filenames (one per line)")
        
        # Initialize processor
        processor = CodeProcessor()
        
        # Show model information
        info = processor.get_model_info()
        console.print(f"[cyan]Using model:[/cyan] [green]{info.get('model', 'Unknown')}[/green]")
        console.print(f"[cyan]      Files:[/cyan] [green]{', '.join(str(f) for f in file_paths)}[/green]")
        
        # Create output directory if specified
        output_directory = None
        if output_dir:
            output_directory = Path(output_dir)
            output_directory.mkdir(parents=True, exist_ok=True)
        # Track processed files
        total_files = len(file_paths)
        files_processed = 0       

        # Process each file
        for i, file in enumerate(file_paths):
            # Apply delay between files (not before the first file)
            if i > 0 and delay > 0:
                console.print(f"[yellow]Waiting {delay} seconds before processing next file...[/yellow]")
                time.sleep(delay)
                
            console.print(f"[bold blue]Processing {file}...[/bold blue]")
            
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
                task = progress.add_task(f"Processing {file.name}...", total=None)
                modified_code = processor.process(original_code, prompt)
                progress.update(task, completed=100)
            
            # Show diff if preview mode or different output file
            diff = create_diff_view(original_code, modified_code)
            console.print(diff)
            
            if preview:
                continue
            
            # Determine output file path
            output_file = file
            if output_directory:
                output_file = output_directory / file.name
            
            # Write output
            with open(output_file, 'w') as f:
                f.write(modified_code)
            
            files_processed += 1
            files_remaining = total_files - files_processed
            console.print(f"[green]Successfully wrote changes to {output_file}[/green]")
            console.print(f"[cyan]Progress: {files_processed}/{total_files} files processed ({files_remaining} remaining)[/cyan]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()
