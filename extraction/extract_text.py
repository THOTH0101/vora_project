import enum

import pymupdf
import re


def extract_pdf_text(path: str) -> list[dict]:
    """extract text from pdf"""
    doc = pymupdf.open(path)
    extracted_pages = []

    for index, page in enumerate(doc):
        text = page.get_text("text")
        extracted_pages.append({"page": index + 1, "text": text.strip()})

    doc.close()
    return extracted_pages


def combine_pages(pages: list[dict]) -> str:
    return "\n\n".join(f"[PAGE {p['page']}]\n{p['text']}" for p in pages)


def clean_text(text: str) -> str:
    # normalize line endings
    text = text.replace("\r\n", "\n")

    # remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # remove common PDF artifacts
    text = text.replace("\x00", "")

    return text.strip()
