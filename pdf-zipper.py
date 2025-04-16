import os
import sys
import argparse
from fpdf import FPDF
import textwrap
from fpdf.enums import XPos, YPos
from urllib.request import urlretrieve

# Constants for font retrieval
FONT_URL = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansMono.ttf"
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSansMono.ttf")


def ensure_font_exists():
    """Ensure the DejaVu Sans Mono font is available and supports Unicode."""
    if not os.path.exists(FONT_PATH):
        print(f"Downloading font to {FONT_PATH}...")
        try:
            urlretrieve(FONT_URL, FONT_PATH)
            print("Font downloaded successfully!")
        except Exception as e:
            print(f"Error downloading font: {e}")
            print("You need to manually download DejaVuSansMono.ttf and place it in the same directory.")
            sys.exit(1)


class CodePDF(FPDF):
    def __init__(self, title="Code Collection", margin=10, line_width=110):
        # Initialize PDF with landscape orientation to support wider lines of code.
        super().__init__(orientation="L", unit="mm", format="A4")

        self.set_margins(left=margin, top=margin, right=margin)
        self.set_auto_page_break(auto=True, margin=margin)
        self.line_width = line_width
        self.add_page()

        try:
            self.add_font("DejaVu", "", FONT_PATH, uni=True)  # Enable Unicode support
            self.set_font("DejaVu", size=8)
        except Exception as e:
            print(f"Error adding font: {e}")
            print("Falling back to Courier")
            self.set_font("Courier", size=8)

        # Add the title to the first page
        self.set_font_size(14)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font_size(8)

    def write_code_block(self, code: str):
        """Writes a block of code to the PDF with proper formatting."""
        line_height = 4
        lines = code.splitlines()

        for line in lines:
            if not line.strip():
                self.cell(0, line_height, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                continue

            if len(line) > self.line_width:
                wrapped_lines = textwrap.wrap(line, width=self.line_width,
                                              subsequent_indent='    ' if line.startswith(' ') else '')
                for wrapped_line in wrapped_lines:
                    self.cell(0, line_height, wrapped_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                self.cell(0, line_height, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def write_file(self, path: str, code: str):
        """Adds a file's content to the PDF."""
        if self.get_y() > self.h - 40:
            self.add_page()

        # Add blue header for file paths
        self.set_fill_color(70, 130, 180)
        self.set_text_color(255, 255, 255)  # White text on blue background
        self.cell(0, 7, f"File: {path}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)  # Reset to black text
        self.write_code_block(code)
        self.cell(0, 5, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def insert_folder_tree(self, folder_structure: str):
        """Insert the folder tree structure into the PDF."""
        self.add_page()
        self.set_font("DejaVu", size=8)
        self.set_text_color(0, 0, 255)  # Blue text for folder structure
        for line in folder_structure.splitlines():
            self.cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)  # Reset to black for other content


def generate_folder_tree(directory: str) -> str:
    """Generate folder tree structure as a string."""
    folder_structure = ""
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level  # Visual indentation for hierarchy
        folder_structure += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            folder_structure += f"{sub_indent}{file}\n"
    return folder_structure


def convert_directory_to_pdf(directory: str, output_path="output.pdf", extensions=None,
                             title="Code Collection", line_width=110, exclude=None, add_tree=False):
    """Convert the code directory into a structured PDF."""
    if extensions is None:
        extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.h', '.hpp',
            '.html', '.css', '.java', '.go', '.rs', '.php', '.rb', '.md',
            '.json', '.yml', '.yaml', '.sh', '.sql', '.xml'
        ]

    if exclude is None:
        exclude = []

    script_path = os.path.abspath(__file__)
    if script_path not in exclude:
        exclude.append(script_path)

    ensure_font_exists()
    pdf = CodePDF(title=title, line_width=line_width)

    # Generate the folder tree and optionally insert it
    if add_tree:
        try:
            folder_structure = generate_folder_tree(directory)
            pdf.insert_folder_tree(folder_structure)
        except Exception as e:
            print(f"Error generating folder tree: {e}")

    processed_files = 0
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)

                if full_path in exclude:
                    print(f"Skipping excluded file: {full_path}")
                    continue

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()
                    if len(code) > 100000:
                        code = code[:50000] + "\n\n... [File truncated due to size] ...\n\n"

                    pdf.write_file(relative_path, code)
                    processed_files += 1
                except Exception as e:
                    print(f"Error processing {relative_path}: {e}")

    try:
        pdf.output(output_path)
        print(f"PDF saved to {output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")
        sys.exit(1)

    return processed_files


def main():
    parser = argparse.ArgumentParser(description="Convert a code directory to a PDF")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to convert (default: current directory)")
    parser.add_argument("-o", "--output", default="code_collection.pdf", help="Output PDF file path")
    parser.add_argument("-t", "--title", default="Code Collection", help="PDF title")
    parser.add_argument("-e", "--extensions", help="Comma-separated list of file extensions to include")
    parser.add_argument("-w", "--width", type=int, default=110, help="Maximum line width in characters")
    parser.add_argument("-x", "--exclude", help="Comma-separated list of files or patterns to exclude")
    parser.add_argument("-i", "--image", action="store_true", help="Include folder tree structure in the PDF")

    args = parser.parse_args()

    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    extensions = None
    if args.extensions:
        extensions = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' for ext in args.extensions.split(',')]

    exclude_list = []
    if args.exclude:
        exclude_list = [os.path.abspath(os.path.join(directory, path.strip())) for path in args.exclude.split(',')]

    try:
        processed = convert_directory_to_pdf(
            directory=directory,
            output_path=args.output,
            extensions=extensions,
            title=args.title,
            line_width=args.width,
            exclude=exclude_list,
            add_tree=args.image
        )
        print(f"Successfully processed {processed} files")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
