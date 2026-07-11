import re
import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
### from markdownify import markdownify as md

from app.config import CORPUS_DIR, EPUB_DIR

# This script processes EPUB files by extracting their html and converting it to markdown.

# Processes an EPUB file extracting only the core text and document data, saving 
#   it as a list of dictionaries, each representing a chapter in the book.
def extract_html_chapters(epub_path: Path
                          ) -> list[dict]:
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
def create_chapter_dictionary(chapter_id: str, 
                              chapter_name: str, 
                              soup: BeautifulSoup
                              ) -> dict:
    chapter_dict = {
        "id": chapter_id,
        "name": chapter_name,
        "soup": soup
        }
    print(f" Extracting:> Chapter ID: {chapter_dict['id']} | Name: {chapter_dict['name']} | Length: {len(chapter_dict['soup'].get_text())} characters")  # Prints the chapter id and name to the console for tracking progress
    return chapter_dict


# <--------- TO WORK ON NEXT ---------------->
def clean_chapters(chapters: list[dict]
                   ) -> list[dict]:
    # Strip out unwanted HTML tags,
    for chapter in chapters:
        soup = chapter["soup"]

        clean_chapters_pageno_helper(soup)
        
        for tag in soup.find_all(["script", "style", "hr", "table"]):
            tag.decompose()
            
        for link in soup.find_all("a"):
            link.unwrap() 
        
        chapter["soup"] = soup
            
    return chapters

def clean_chapters_pageno_helper(soup: BeautifulSoup
                                 ) -> None:
    for span in soup.find_all("span", class_="x-ebookmaker-pageno"):
        page_id = span.get("id", "")
        match = re.search(r"Page_(\d+)", page_id)
        if match:
            page_number = match.group(1)
            comment = f"\n<!-- page: {page_number} -->\n\n"
        else:
            comment = "\n\n"
        if span.parent:
            span.replace_with(comment)
        else:
            span.decompose()
            
    
# <--------- CONVERT TO MARKDOWN ------------->

# <--------- SAVE PROCESSED CHAPTERS --------->
def save_chapters_as_markdown(chapters: list[dict], 
                              output_dir: Path
                              ) -> None:
    ### book = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        output_file = output_dir / f"{chapter['name']}.html"            #!!!!!!!!!!!!file extension MUST be changed to .md in finalized version of the pipeline
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(chapter["soup"]))


def main() -> None:
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")
        
    output_dir = CORPUS_DIR / "html" / epub_path.stem

    unprocessed_chapters = extract_html_chapters(epub_path)
    print(f"Extracted {len(unprocessed_chapters)} chapters from {epub_path.name}")
    processed_chapters = clean_chapters(unprocessed_chapters)
    print(f"Processed {len(processed_chapters)} chapters from {epub_path.name}")
    save_chapters_as_markdown(processed_chapters, output_dir)


### TO REMOVE ####

##################

    # chapters will be used to create a markdown version of the book in the next step of the pipeline


if __name__ == "__main__":
    main()