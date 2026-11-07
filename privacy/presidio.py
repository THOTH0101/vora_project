from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer

from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine

from nlp.engine import get_nlp


class LoadedSpacyNlpEngine(SpacyNlpEngine):
    def __init__(self, loaded_spacy_model):

        super().__init__()

        # Reuse the existing spaCy instance.
        self.nlp = {"en": loaded_spacy_model}


def create_presidio():

    shared_nlp = get_nlp()

    nlp_engine = LoadedSpacyNlpEngine(loaded_spacy_model=shared_nlp)

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

    # Add Nigerian telephone number recognition.
    nigeria_phone = PatternRecognizer(
        supported_entity="NIGERIAN_PHONE_NUMBER",
        patterns=[
            Pattern(
                name="nigeria_mobile",
                regex=r"\b(?:\+234|234|0)[ -]?(?:70|80|81|90|91)\d{8}\b",
                score=0.85,
            )
        ],
        supported_language="en",
    )

    analyzer.registry.add_recognizer(nigeria_phone)

    anonymizer = AnonymizerEngine()

    return analyzer, anonymizer


# Initialize once per worker process.
analyzer, anonymizer = create_presidio()
