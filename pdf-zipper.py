import os
import sys
import argparse
from fpdf import FPDF
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name
from pathlib import Path
import tempfile
import shutil
from urllib.request import urlretrieve
import textwrap

# Путь к шрифту DejaVu Sans Mono
FONT_URL = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSansMono.ttf"
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DejaVuSansMono.ttf")

def ensure_font_exists():
    """Убедиться, что шрифт DejaVu Sans Mono доступен"""
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
        # Установим параметры страницы - ландшафтная ориентация для более широких строк
        super().__init__(orientation="L", unit="mm", format="A4")
        
        # Установим меньшие поля
        self.set_margins(left=margin, top=margin, right=margin)
        self.set_auto_page_break(auto=True, margin=margin)
        
        # Сохраним максимальную ширину строки в символах
        self.line_width = line_width
        
        # Добавим первую страницу
        self.add_page()
        
        # Добавим шрифт
        try:
            self.add_font("DejaVu", "", FONT_PATH)
            self.set_font("DejaVu", size=8)  # Уменьшим размер шрифта
        except Exception as e:
            print(f"Error adding font: {e}")
            print("Falling back to Courier")
            self.set_font("Courier", size=8)
        
        # Добавляем заголовок
        self.set_font_size(14)
        self.cell(0, 10, title, align="C")
        self.ln(10)
        self.set_font_size(8)  # Вернемся к маленькому размеру шрифта

    def write_code_block(self, code: str):
        line_height = 4  # Небольшая высота строки для плотного текста
        
        # Разобьем код на строки
        lines = code.splitlines()
        
        for line in lines:
            # Проверка на пустую строку
            if not line.strip():
                self.ln(line_height)
                continue
            
            # Если строка длиннее максимальной ширины, разбиваем её
            if len(line) > self.line_width:
                # Разбиваем длинную строку на части
                wrapped_lines = textwrap.wrap(line, width=self.line_width, 
                                             subsequent_indent='    ' if line.startswith(' ') else '')
                
                # Печатаем каждую часть на отдельной строке
                for i, wrapped_line in enumerate(wrapped_lines):
                    # Для первой строки используем обычный отступ
                    if i == 0:
                        self.set_fill_color(245, 245, 245)
                        self.cell(0, line_height, wrapped_line, ln=1, fill=True)
                    # Для продолжений строки добавим индикатор переноса
                    else:
                        self.set_fill_color(240, 240, 250)  # Слегка другой оттенок для продолжений
                        self.cell(0, line_height, wrapped_line, ln=1, fill=True)
            else:
                # Короткие строки печатаем как обычно
                self.set_fill_color(245, 245, 245)
                self.cell(0, line_height, line, ln=1, fill=True)

    def write_file(self, path: str, code: str):
        # Добавим проверку на необходимость новой страницы
        if self.get_y() > self.h - 40:
            self.add_page()
        
        # Заголовок файла
        self.set_fill_color(70, 130, 180)  # Steel Blue
        self.set_text_color(255, 255, 255)  # Белый текст
        self.cell(0, 7, f"File: {path}", ln=1, fill=True)
        self.ln(1)
        
        # Содержимое файла
        self.set_text_color(0, 0, 0)  # Черный текст
        self.write_code_block(code)
        self.ln(5)  # Добавляем отступ между файлами

def get_file_extensions():
    """Возвращает список расширений файлов для обработки"""
    return [
        '.py', '.js', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.h', '.hpp',
        '.html', '.css', '.java', '.go', '.rs', '.php', '.rb', '.md',
        '.json', '.yml', '.yaml', '.sh', '.sql', '.xml'
    ]

def convert_directory_to_pdf(directory: str, output_path="output.pdf", extensions=None, title="Code Collection", line_width=110, exclude=None):
    """Преобразует директорию с кодом в PDF с корректным переносом длинных строк"""
    if extensions is None:
        extensions = get_file_extensions()
    
    # Initialize exclude list if not provided
    if exclude is None:
        exclude = []
    
    # Get absolute path of script to exclude it
    script_path = os.path.abspath(__file__)
    # Add the script itself to exclusion list if not already there
    if script_path not in exclude:
        exclude.append(script_path)
    
    ensure_font_exists()
    
    # Создаем экземпляр PDF с передачей параметра максимальной ширины строки
    pdf = CodePDF(title=title, line_width=line_width)
    processed_files = 0
    skipped_files = 0
    
    # Собираем все подходящие файлы
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in sorted(files):  # Сортируем файлы для более предсказуемого порядка
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.abspath(os.path.join(root, file))
                
                # Skip files in exclude list
                if full_path in exclude:
                    print(f"Skipping excluded file: {full_path}")
                    skipped_files += 1
                    continue
                
                # Skip the script itself
                if full_path == script_path:
                    print(f"Skipping the PDF-zipper script itself: {full_path}")
                    skipped_files += 1
                    continue
                
                relative_path = os.path.relpath(full_path, directory)
                files_to_process.append((full_path, relative_path))
    
    total_files = len(files_to_process)
    print(f"Found {total_files} files to process ({skipped_files} files excluded)")
    
    # Обрабатываем файлы
    for i, (full_path, relative_path) in enumerate(files_to_process):
        print(f"Processing {i+1}/{total_files}: {relative_path}")
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            
            # Проверяем, не слишком ли большой файл
            if len(code) > 100000:  # Ограничим очень большие файлы
                code = code[:50000] + "\n\n... [File truncated due to size] ...\n\n"
                
            pdf.write_file(relative_path, code)
            processed_files += 1
        except Exception as e:
            print(f"Error processing {relative_path}: {e}")
    
    # Добавляем информацию в конец документа
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, f"Processed {processed_files} files from {directory}", ln=1)
    pdf.cell(0, 5, f"Generated by PDF Code Zipper", ln=1)
    
    # Сохраняем результат
    try:
        pdf.output(output_path)
        print(f"PDF saved to {output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")
        print("Try changing the output filename or directory.")
        
    return processed_files

def main():
    parser = argparse.ArgumentParser(description="Convert code directory to PDF for AI context")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to convert (default: current directory)")
    parser.add_argument("-o", "--output", default="code_collection.pdf", help="Output PDF file path")
    parser.add_argument("-t", "--title", default="Code Collection", help="PDF title")
    parser.add_argument("-e", "--extensions", help="Comma-separated list of file extensions to include")
    parser.add_argument("-w", "--width", type=int, default=110, help="Maximum line width in characters")
    parser.add_argument("-x", "--exclude", help="Comma-separated list of files or patterns to exclude")
    
    args = parser.parse_args()
    
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    extensions = None
    if args.extensions:
        extensions = [ext.strip() if ext.strip().startswith('.') else f'.{ext.strip()}' 
                     for ext in args.extensions.split(',')]
    
    # Process exclusion patterns
    exclude_list = []
    if args.exclude:
        # Convert comma-separated string to list of paths
        raw_excludes = [path.strip() for path in args.exclude.split(',')]
        
        # Convert relative paths to absolute paths
        for path in raw_excludes:
            if os.path.isabs(path):
                exclude_list.append(path)
            else:
                exclude_list.append(os.path.abspath(os.path.join(directory, path)))
    
    # Always add the script itself to exclude list
    script_path = os.path.abspath(__file__)
    if script_path not in exclude_list:
        exclude_list.append(script_path)
    
    try:
        processed = convert_directory_to_pdf(
            directory=directory,
            output_path=args.output,
            extensions=extensions,
            title=args.title,
            line_width=args.width,
            exclude=exclude_list
        )
        
        print(f"Successfully processed {processed} files")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()