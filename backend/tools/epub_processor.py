import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from app.config import CORPUS_DIR, EPUB_DIR

# This script processes EPUB files by extracting their html content
# Preliminary step to investigate html structure before stripping html tags and converting to markdown

def process_epub(epub_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    book = epub.read_epub(str(epub_path))
    
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content()
        output_file_path = output_dir / f"{item.get_name()}.html"
        output_file_path.write_bytes(content)


def main():
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")
        
    output_dir = CORPUS_DIR / "html" / epub_path.stem

    process_epub(epub_path, output_dir)

if __name__ == "__main__":
    main()