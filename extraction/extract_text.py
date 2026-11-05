import pymupdf


def extract_pdf_text(path: str) -> str:
    # use to extract text from pdf
    doc = pymupdf.open(path)
    extracted_pages = []

    for page in doc:
        text = page.get_text("text")

        # Fall back to OCR when a page has little
        # or no extractable text.
        if len(text.strip()) < 40:
            text_page = page.get_textpage_ocr(language="eng", dpi=300, full=True)
            text = page.get_text("text", textpage=text_page)

        extracted_pages.append(text)

    doc.close()
    return "\n".join(extracted_pages)
