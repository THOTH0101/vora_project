import io
import json
import unittest
from unittest.mock import Mock, patch

import main
import run_extract
from extraction.llm import GeminiExtractionError
from schemas.candidate import CandidateProfile


class PipelineTests(unittest.TestCase):
    def test_pipeline_sends_only_redacted_text_and_safe_entities_to_gemini(self):
        raw = "[PAGE 1]\nJane Doe\nRegistered Nurse\njane@example.test"
        redacted = raw.replace("Jane Doe", "<PERSON>").replace(
            "jane@example.test", "<EMAIL_ADDRESS>"
        )
        name_start, nurse_start = raw.index("Jane Doe"), raw.index("Registered Nurse")
        email_start = raw.index("jane@example.test")
        entities = [
            {"text": "Jane Doe", "label": "PERSON", "start": name_start, "end": name_start + 8},
            {
                "text": "Registered Nurse", "label": "PROFESSION",
                "start": nurse_start, "end": nurse_start + 16,
            },
            {
                "text": "jane@example.test", "label": "ORG",
                "start": email_start, "end": email_start + 17,
            },
        ]
        privacy = {"redacted_text": redacted, "pii": [
            {"type": "PERSON", "value": "Jane Doe", "start": name_start, "end": name_start + 8},
            {
                "type": "EMAIL_ADDRESS", "value": "jane@example.test",
                "start": email_start, "end": email_start + 17,
            },
        ]}
        profile = CandidateProfile(identity={"primary_group": "nursing"}, location={})
        calls = Mock()
        with (
            patch(
                "run_extract.extract_pdf_text",
                return_value=[{"page": 1, "text": raw.split("\n", 1)[1]}],
            ) as pdf,
            patch("run_extract.extract_cv_entities", return_value=entities) as nlp,
            patch("run_extract.protect_cv_text", return_value=privacy) as presidio,
            patch("run_extract.extract_candidate_profile", return_value=profile) as gemini,
        ):
            for name, mock in (
                ("pdf", pdf), ("nlp", nlp), ("presidio", presidio), ("gemini", gemini)
            ):
                calls.attach_mock(mock, name)
            details = run_extract.extract_doc_details("synthetic.pdf", professional_group="nursing")
            nlp.assert_called_once_with(raw)
            presidio.assert_called_once_with(raw)
            gemini.assert_called_once_with(
                redacted,
                professional_group="nursing",
                entities=[{"text": "Registered Nurse", "label": "PROFESSION", "page": 1}],
            )
        self.assertEqual(
            [call[0] for call in calls.mock_calls], ["pdf", "nlp", "presidio", "gemini"]
        )
        self.assertEqual(details["candidate_profile"], profile.model_dump(mode="json"))
        self.assertIs(details["PII_result"], privacy)
        self.assertIs(details["entities_extracted"], entities)

    def test_empty_or_scanned_pdf_is_rejected_before_nlp_and_gemini(self):
        with (
            patch("run_extract.extract_pdf_text", return_value=[{"page": 1, "text": " \n"}]),
            patch("run_extract.extract_cv_entities") as nlp,
            patch("run_extract.extract_candidate_profile") as gemini,
        ):
            with self.assertRaisesRegex(ValueError, "no extractable text"):
                run_extract.extract_doc_details("scanned.pdf")
            nlp.assert_not_called()
            gemini.assert_not_called()


class CommandLineTests(unittest.TestCase):
    def test_stdout_contains_candidate_json_without_local_pii(self):
        profile = CandidateProfile(identity={}, location={}).model_dump(mode="json")
        details = {"candidate_profile": profile, "PII_result": {"pii": [{"value": "Jane Doe"}]}}
        output = io.StringIO()
        with (
            patch("sys.argv", ["main.py", "synthetic.pdf", "--professional-group", "nursing"]),
            patch("main.extract_doc_details", return_value=details) as extract,
            patch("sys.stdout", output),
        ):
            self.assertEqual(main.main(), 0)
        self.assertEqual(json.loads(output.getvalue()), profile)
        self.assertNotIn("Jane Doe", output.getvalue())
        extract.assert_called_once_with("synthetic.pdf", professional_group="nursing")

    def test_extraction_errors_have_nonzero_exit_and_stderr(self):
        output, error = io.StringIO(), io.StringIO()
        with (
            patch("sys.argv", ["main.py", "synthetic.pdf"]),
            patch(
                "main.extract_doc_details",
                side_effect=GeminiExtractionError("Set GEMINI_API_KEY"),
            ),
            patch("sys.stdout", output),
            patch("sys.stderr", error),
        ):
            self.assertEqual(main.main(), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("GEMINI_API_KEY", error.getvalue())


if __name__ == "__main__":
    unittest.main()
