from extraction.extract_text import clean_text, combine_pages, extract_pdf_text
from extraction.llm import extract_candidate_profile
from nlp.engine import extract_cv_entities
from privacy.entity_hints import build_entity_hints
from privacy.presidio import protect_cv_text


def extract_doc_details(path: str, professional_group: str = "unknown") -> dict:
    # 1. Extract PDF content
    pages = extract_pdf_text(path)
    if not any(page["text"].strip() for page in pages):
        raise ValueError("PDF has no extractable text; scanned CVs require OCR")
    raw_text = clean_text(combine_pages(pages))

    # 2. Run shared NLP model
    entities = extract_cv_entities(raw_text)

    # 3. Detect and redact PII
    privacy_result = protect_cv_text(raw_text)

    # 4. Extract structured CV information
    entity_hints = build_entity_hints(
        original_text=raw_text,
        redacted_text=privacy_result["redacted_text"],
        entities=entities,
        pii=privacy_result["pii"],
    )
    profile = extract_candidate_profile(
        privacy_result["redacted_text"],
        professional_group=professional_group,
        entities=entity_hints,
    )
    # Original entities and recovered PII remain local to the caller.
    return {
        "PII_result": privacy_result,
        "entities_extracted": entities,
        "candidate_profile": profile.model_dump(mode="json"),
    }
