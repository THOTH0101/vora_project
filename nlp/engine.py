import spacy

from functools import lru_cache
from nlp.patterns import CV_PATTERNS


@lru_cache(maxsize=1)
def get_nlp():

    nlp = spacy.load("en_core_web_lg")

    # Keep CV entities separate from the standard NER
    # entities to avoid overlapping-span conflicts.
    ruler = nlp.add_pipe(
        "span_ruler",
        name="cv_span_ruler",
        config={"spans_key": "cv_entities", "annotate_ents": False},
    )

    ruler.add_patterns(CV_PATTERNS)

    return nlp


def extract_cv_entities(text: str):

    doc = get_nlp()(text)

    entities = []

    for ent in doc.ents:
        entities.append(
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
        )

    for ent in doc.spans.get("cv_entities", []):
        entities.append(
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
        )

    return entities
