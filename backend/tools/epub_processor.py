import re
import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
### from markdownify import markdownify as md

from app.config import CORPUS_DIR, EPUB_DIR

# This script processes EPUB files by extracting their html and converting it to markdown.

# Processes an EPUB file extracting only the core text and document data, saving 
#   it as a list of dictionaries, each representing a chapter in the book.

PAGE_SPAN_CLASS = "x-ebookmaker-pageno"
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)")
# SUBSECTION_RE = re.compile(r"^\((\d+)\)\s+(.+)")
SUBSECTION_RE = re.compile(r"^\s*\((\d+)\)\s*$")

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

# <--------- HELPER FUNCTIONS ---------------->

def clean_chapters(chapters: list[dict]
                   ) -> list[dict]:
    # Strip out unwanted HTML tags,
    for chapter in chapters:
        soup = chapter["soup"]

        clean_chapters_pageno_helper(soup)
        
        for tag in soup.find_all(["script", "style", "hr", "table"]):
            tag.decompose()

        for footnotes in soup.find_all("div", class_="footnotes"):
            footnotes.decompose()

        for anchor in soup.find_all("a", class_="fnanchor"):
            anchor.decompose()

        for article in soup.find_all("h3"):
            article.attrs = {}
            
        for link in soup.find_all("a"):
            link.unwrap() 
        
        for header in soup.find_all(["h4", "h5"]):
            header.unwrap()

        clean_sections_helper(soup)
        clean_subsections_helper(soup)
        
        for tag in soup.find_all(["span"]):
            tag.unwrap()
        
        chapter["soup"] = soup

            
    return chapters

def clean_chapters_pageno_helper(soup: BeautifulSoup
                                 ) -> None:
    for span in soup.find_all("span", class_=PAGE_SPAN_CLASS):
        page_id = span.get("id", "")
        match = re.search(r"Page_(\d+)", page_id)
        if match and span.parent:
            comment = Comment(f" page: {match.group(1)} ")
            span.replace_with(NavigableString("\n\n"), comment, NavigableString("\n\n"))
        else:
            span.decompose()

def clean_sections_helper(soup: BeautifulSoup
                                 ) -> None:
    for span in soup.select('p > b > span[id^="sec_"]'):
        b = span.parent
        if not b:
            continue
        p = b.parent
        if not p:
            continue

        b_text = " ".join(b.get_text().split())
        match = SECTION_RE.match(b_text)
        if not match:
            continue

        section_num, section_title = match.groups()
        h4 = soup.new_tag("h4")
        h4.string = f"{section_num}. {section_title}"

        p.insert_before(h4)

        b.decompose()

        if not p.get_text(strip=True): p.decompose()

# <--------- TO WORK ON NEXT ---------------->
def clean_subsections_helper(soup: BeautifulSoup
                             ) -> None:
    for p in list(soup.find_all("p")):
        contents = p.contents
        if len(contents) < 2: continue
        
        first_child = contents[0]
        second_child = contents[1]
        if not isinstance(first_child, NavigableString): continue

        match = SUBSECTION_RE.match(str(first_child))
        if not match or not isinstance(second_child, Tag): continue

        subsection_num = match.group(1)
        subsection_title = " ".join(second_child.get_text().split())

        h5 = soup.new_tag("h5")
        h5.string = f"({subsection_num}) {subsection_title}"

        p.insert_before(h5)

        first_child.extract()
        second_child.decompose()

        if not p.get_text(strip=True): p.decompose()

def clean_clauses_helper(soup: BeautifulSoup
                             ) -> None:
    return
           
    
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