import unittest

from privacy.entity_hints import build_entity_hints, sanitize_entity_hints


def entity(text, value, label):
    start = text.index(value)
    return {"text": value, "label": label, "start": start, "end": start + len(value)}


class EntityHintTests(unittest.TestCase):
    def test_pii_overlap_is_removed_even_if_spacy_labels_it_as_an_organisation(self):
        original = "[PAGE 1]\nJane Doe\nJane Doe Hospital\nRegistered Nurse"
        redacted = "[PAGE 1]\n<PERSON>\n<PERSON> Hospital\nRegistered Nurse"
        entities = [
            entity(original, "Jane Doe", "PERSON"),
            entity(original, "Jane Doe Hospital", "ORG"),
            entity(original, "Registered Nurse", "PROFESSION"),
        ]
        spans = [
            {"start": original.index("Jane Doe"), "end": original.index("Jane Doe") + 8},
            {
                "start": original.index("Jane Doe Hospital"),
                "end": original.index("Jane Doe Hospital") + 8,
            },
        ]
        self.assertEqual(
            build_entity_hints(original, redacted, entities, spans),
            [{"text": "Registered Nurse", "label": "PROFESSION", "page": 1}],
        )

    def test_original_offsets_become_correct_pages_after_redaction_changes_length(self):
        original = "[PAGE 1]\nAlexandra Morgan\n[PAGE 2]\nExample Hospital\n2020"
        redacted = original.replace("Alexandra Morgan", "<PERSON>")
        entities = [
            entity(original, "Example Hospital", "ORG"),
            entity(original, "2020", "DATE"),
        ]
        hints = build_entity_hints(original, redacted, entities, [])
        self.assertEqual([hint["page"] for hint in hints], [2, 2])
        self.assertEqual([hint["text"] for hint in hints], ["Example Hospital", "2020"])
        self.assertTrue(all(set(hint) == {"text", "label", "page"} for hint in hints))

    def test_invalid_original_spans_cannot_be_forwarded(self):
        text = "[PAGE 1]\nRegistered Nurse"
        valid = entity(text, "Registered Nurse", "PROFESSION")
        entities = [
            {**valid, "start": -1},
            {**valid, "end": len(text) + 1},
            {**valid, "text": "Jane Doe"},
            {"text": "Registered Nurse", "label": "PROFESSION"},
        ]
        self.assertEqual(build_entity_hints(text, text, entities, []), [])

    def test_direct_hints_are_grounded_deduplicated_and_stripped_of_extra_fields(self):
        text = "[PAGE 1]\n<PERSON>\nRegistered Nurse at Example Hospital"
        hints = sanitize_entity_hints(
            [
                {"text": "Jane Doe", "label": "ORG", "page": 1},
                {"text": "Example Hospital", "label": "PERSON", "page": 1},
                {"text": "<PERSON>", "label": "ORG", "page": 1},
                {
                    "text": "Registered Nurse", "label": "PROFESSION", "page": 1,
                    "value": "jane@example.test", "start": 999,
                },
                {"text": "Registered Nurse", "label": "PROFESSION", "page": 1},
            ],
            text,
        )
        self.assertEqual(hints, [{"text": "Registered Nurse", "label": "PROFESSION", "page": 1}])


if __name__ == "__main__":
    unittest.main()
