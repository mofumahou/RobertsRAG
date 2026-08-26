import re
import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from markdownify import markdownify as md # TO BE DELETED

from app.config import CORPUS_DIR, EPUB_DIR

# Processes an EPUB file extracting only the html and document data, saving 
# it as a list of dictionaries, each representing a chapter in the book.

PAGE_SPAN_CLASS = "x-ebookmaker-pageno"
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)")
SUBSECTION_RE = re.compile(r"^\s*\((\d+)\)\s*$")
CHAPTER_ID_RE = re.compile(r"h-\d{1,2}")

# Pull the html content of each chapter in the EPUB file, returning a list of dictionaries
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
            body = soup.find("body")

            if body: soup = body

            match = CHAPTER_ID_RE.search(item.get_name())
            chapter_id = match.group(0) if match else item.get_id()

            chapters.append(create_chapter_dictionary(chapter_id, item.get_name(), soup))
            print(f"Extracted chapter {item.get_name()} with id {chapter_id}")
    return chapters

# Creates a dictionary for each chapter in the EPUB file, preserving the chapter id, name, and content (as a BeautifulSoup object)
def create_chapter_dictionary(chapter_id: str, 
                              chapter_name: str, 
                              soup: BeautifulSoup
                              ) -> dict:
    chapter_dict = {
        "chapter_id": chapter_id,
        "chapter_name": chapter_name,
        "soup": soup
        }
    return chapter_dict

# Main formatter function
def clean_chapters(chapters: list[dict]
                   ) -> list[dict]:
    # Main function to clean the html content of each chapter
    for chapter in chapters:
        soup = chapter["soup"]

        # Convert page spans to soup comments
        clean_chapters_pageno_helper(soup)

        # Remove unwanted tags and attributes
        for tag in soup.find_all(["script", "style", "hr", "table"]):
            tag.decompose()
        for footnotes in soup.find_all("div", class_="footnotes"):
            footnotes.decompose()
        for anchor in soup.find_all("a", class_="fnanchor"):
            anchor.decompose()

        # Unwrap links and h4/h5 for a clean section/subsection template
        for link in soup.find_all("a"):
            link.unwrap() 
        
        for header in soup.find_all(["h4", "h5"]):
            header.unwrap()

        # Call helper functions to format the chapters into a clean structure with proper header tags
        clean_parts_helper(soup)
        clean_articles_helper(soup)
        clean_sections_helper(soup)
        clean_subsections_helper(soup)

        # Remove last bit of noise
        for tag in soup.find_all(["span"]):
            tag.unwrap()

        # Match all tags and remove all attributes
        for tag in soup.find_all(True):
            tag.attrs = {}
                    
        chapter["soup"] = soup
    return chapters

# <--------- HELPER FUNCTIONS ---------------->
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
    return


def clean_articles_helper(soup: BeautifulSoup
                          ) -> None:
    for article in list(soup.find_all("h3")):
        article.string = article.get_text(strip=True).removesuffix(".")
    return


def clean_parts_helper(soup: BeautifulSoup
                       ) -> None:
    # extract title and replace h2 text with it
    for part in list(soup.find_all("h2")):
        h2_title = part.attrs.get("title")
        if h2_title is not None:
            part.string = h2_title.removesuffix(".")
        else:
            continue
    return


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
        h4.string = f"{section_num}. {section_title}".removesuffix(".")

        p.insert_before(h4)

        b.decompose()

        if not p.get_text(strip=True): p.decompose()
    return


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
        h5.string = f"({subsection_num}) {subsection_title}".removesuffix(".")

        p.insert_before(h5)

        first_child.extract()
        second_child.decompose()

        if not p.get_text(strip=True): p.decompose()
    return

# <--------- (TO BE DELETED) SAVE PROCESSED CHAPTERS --------->
# Purely for debugging purposes
def save_chapters(chapters: list[dict],
                  output_dir: Path
                  ) -> None:
    ### book = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        output_file = output_dir / f"{chapter['chapter_name']}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(chapter["soup"]))
        markdown_output_file = output_dir / f"{chapter['chapter_name']}.md"
        with open(markdown_output_file, "w", encoding="utf-8") as f:
            f.write(md(str(chapter["soup"]), heading_style="ATX"))
    return

# <--------- (TO BE MODIFIED) MAIN FUNCTION --------->
# Needs changing to integrate with ingestion_pipeline.py, no files will be generated in final version
# Instead the processed chapters will be returned to ingestion_pipeline.py for chunking, embedding, and storage.
def main() -> None:
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")
        
    output_dir = CORPUS_DIR / "html" / epub_path.stem

    unprocessed_chapters = extract_html_chapters(epub_path)
    print(f"Extracted {len(unprocessed_chapters)} chapters from {epub_path.name}")
    processed_chapters = clean_chapters(unprocessed_chapters)
    print(f"Processed {len(processed_chapters)} chapters from {epub_path.name}")
    save_chapters(processed_chapters, output_dir)


if __name__ == "__main__":
    main()