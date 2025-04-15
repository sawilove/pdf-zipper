# PDF-Zipper

## Overview

PDF-Zipper is a command-line tool that converts your code project into a formatted PDF document. It's specifically designed to create PDFs that are optimal for AI analysis, code review, or documentation purposes.

## Features

- **Project Directory Conversion**: Transforms all code files in a directory (and subdirectories) into a single PDF
- **Code Formatting**: Preserves code indentation and handles long lines with proper wrapping
- **Selective File Processing**: Filter files by extension or exclude specific files/directories
- **Visual Structure**: Files are clearly separated with headers and consistent formatting
- **AI-Friendly Format**: Creates PDFs that are easily digestible by AI assistants for context loading

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - fpdf
  - pygments

### Setup

1. Clone this repository or download the script:
   ```bash
   git clone https://github.com/yourusername/pdf-zipper.git
   cd pdf-zipper
   ```

2. Install required dependencies:
   ```bash
   pip install fpdf pygments
   ```

## Usage

### Basic Usage

```bash
python pdf-zipper.py [directory]
```

This will create a `code_collection.pdf` file in the current directory containing all supported code files.

### Advanced Options

```bash
python pdf-zipper.py [directory] -o output.pdf -t "Project Title" -w 120 -e ".py,.js,.html" -x "node_modules/,venv/"
```

### Command Line Arguments

| Option | Long Option | Description |
|--------|-------------|-------------|
| | `directory` | Directory to convert (default: current directory) |
| `-o` | `--output` | Output PDF file path (default: code_collection.pdf) |
| `-t` | `--title` | PDF title (default: "Code Collection") |
| `-e` | `--extensions` | Comma-separated list of file extensions to include |
| `-w` | `--width` | Maximum line width in characters (default: 110) |
| `-x` | `--exclude` | Comma-separated list of files or patterns to exclude |

## Supported File Types

The tool supports most common programming and markup languages including:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- HTML/CSS (.html, .css)
- C/C++ (.c, .cpp, .h, .hpp)
- Java (.java)
- Go (.go)
- Rust (.rs)
- PHP (.php)
- Ruby (.rb)
- Markdown (.md)
- Configuration files (.json, .yml, .yaml)
- Shell scripts (.sh)
- SQL (.sql)
- XML (.xml)

## Examples

### Create a PDF of a Python project
```bash
python pdf-zipper.py ~/projects/my-python-app -o python-project.pdf -t "My Python Project" -e ".py,.md"
```

### Export a web project excluding node_modules
```bash
python pdf-zipper.py ~/projects/web-app -x "node_modules/,dist/,build/" -e ".js,.html,.css,.jsx"
```

## Notes

- The script automatically excludes itself from the PDF
- Very large files (>100KB) will be truncated in the output
- The tool automatically downloads a monospace font for best results

## Troubleshooting

- If you encounter font issues, manually download DejaVuSansMono.ttf and place it in the same directory as the script
- For errors with large projects, try excluding unnecessary directories
