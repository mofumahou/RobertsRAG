import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
### from markdownify import markdownify as md

from app.config import CORPUS_DIR, EPUB_DIR

# This script processes EPUB files by extracting their html and converting it to markdown.

# Processes an EPUB file extracting only the core text and document data, saving 
#   it as a list of dictionaries, each representing a chapter in the book.
def extract_html_chapters(epub_path: Path) -> list[dict]:
    book = epub.read_epub(str(epub_path))
    
    # Strips out front matter and back matter, keeps only the main content of the book
    document_ids_to_skip = {"pg-header", 
                            "cover", 
                            "item4", 
                            "item5", 
                            "ENDNOTE", 
                            "pg-footer", 
                            "ncx", 
                            "coverpage-wrapper"}
    
    document = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    chapters = []

    for item in document:
        if item.get_id() not in document_ids_to_skip:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            chapters.append(create_chapter_dictionary(item.get_id(), item.get_name(), soup))
    return chapters


# Creates a dictionary for each chapter in the EPUB file, preserving the chapter id, name, and content (as a BeautifulSoup object)
def create_chapter_dictionary(chapter_id: str, chapter_name: str, soup: BeautifulSoup) -> dict:
    chapter_dict = {
        "id": chapter_id,
        "name": chapter_name,
        "content": soup
        }
    print(f" Extracting:> Chapter ID: {chapter_dict['id']} | Name: {chapter_dict['name']} | Length: {len(chapter_dict['content'].get_text())} characters")  # Prints the chapter id and name to the console for tracking progress
    return chapter_dict


# <--------- TO WORK ON NEXT --------->
def clean_chapters(chapters: list[dict]) -> str:
    # Strip out unwanted HTML tags, 
    pass


def main() -> None:
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")
        
    output_dir = CORPUS_DIR / "html" / epub_path.stem
    chapters = extract_html_chapters(epub_path)
    # chapters will be used to create a markdown version of the book in the next step of the pipeline


if __name__ == "__main__":
    main()