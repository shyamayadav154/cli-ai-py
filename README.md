# code-edit

An AI-powered command-line tool for intelligent code editing and transformation.

## Features

- Quick code refactoring using natural language prompts
- Support for multiple programming languages
- Preview changes before applying them
- Backup creation for safety
- Rich diff view of proposed changes

## Installation

```bash
pip install code-edit
```

## Usage

Basic usage:
```bash
code-edit --prompt "Add input validation for email fields" --file src/form.js
```

Preview changes without applying them:
```bash
code-edit --prompt "Convert to async/await syntax" --file src/utils.js --preview
```

Use a prompt file for complex changes:
```bash
code-edit --prompt-file instructions.txt --file src/api/endpoints.py
```

Save changes to a new file:
```bash
code-edit --prompt "Add error handling" --file src/service.js --output src/service.new.js
```

## Options

- `--prompt TEXT`: Natural language description of desired changes
- `--prompt-file FILE`: File containing the change description
- `--file FILE`: Target code file to modify
- `--output FILE`: Output file (defaults to modifying input file)
- `--preview`: Show changes without applying them
- `--backup`: Create a backup before modifying the file
- `--help`: Show this help message

## Requirements

- Python 3.8 or higher
- Google API key for AI functionality (get one from https://makersuite.google.com/app/apikey)

## Security

This tool:
- Only processes local files
- Creates backups when requested
- Is transparent about API usage
- Never sends sensitive data

## License

MIT License 