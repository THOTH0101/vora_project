from extraction.extract_text import clean_text, combine_pages, extract_pdf_text
from nlp.engine import extract_cv_entities
from privacy.presidio import protect_cv_text


def extract_doc_details(path: str) -> dict:
    # 1. Extract PDF content
    pages = extract_pdf_text(path)
    raw_text = clean_text(combine_pages(pages))

    # 2. Run shared NLP model
    entities = extract_cv_entities(raw_text)

    # 3. Detect and redact PII
    privacy_result = protect_cv_text(raw_text)

    # 4. Extract structured CV information
    return {"PII_result": privacy_result, "entities_extracted": entities}
