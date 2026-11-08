# Medical CV extraction

The pipeline extracts and cleans PDF text with page markers, extracts spaCy
entities, redacts detected names/email addresses/phone numbers with Presidio,
then asks Gemini for a `CandidateProfile` using the redacted text, filtered
entity hints, and the Pydantic JSON schema.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
bash dependencies.sh
bash model.sh
```

Create `.env` using the keys in `.env.example`, then set `GEMINI_API_KEY`.
`GEMINI_MODEL` defaults to `gemini-3.8-flash` and can be overridden. Environment
variables take precedence over `.env`. Credentials are checked when extraction
is requested, so importing the code does not require an API key.

## Run

```bash
python main.py path/to/cv.pdf --professional-group nursing
```

The profession hint is optional; its default is `unknown`. Standard output is
the validated candidate profile as JSON. Errors go to standard error with a
nonzero exit code.

Python callers can use `extract_doc_details(path, professional_group="unknown")`.
The returned dictionary contains `candidate_profile`, plus the original local
`PII_result` and `entities_extracted`. Only the redacted CV and filtered entity
hints go to Gemini. Entities overlapping detected PII are removed, and original
character offsets are replaced by source page numbers.

## Prompt and validation

`extraction/prompt.py` maintains one medical extraction system instruction and
profession-specific guidance. It defines the CV as the source of truth, treats
spaCy entities as suggestions, preserves incomplete dates, distinguishes licence
claims from verification, and keeps unsupported values empty. Redacted values
cannot become profile field values.

Gemini uses schema-constrained JSON output through the supported
`models.generate_content` API. The sampling parameters are left at their model
defaults, as Gemini 3.8 ignores custom temperature/top-p/top-k settings. The
response is checked for blocking/truncation, validated with Pydantic, and checked
for exact evidence quotes on the stated pages. Experience summaries stay empty
for downstream calculation.

These checks establish format and quotation provenance. Field accuracy and
completeness require evaluation against labeled CVs across the supported
professions. The schema currently has no dedicated general certification or
publication section; extend it if those need separate records. PDF extraction
currently reads embedded text and does not perform OCR on scanned CVs.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use mocked Gemini responses and a local SDK HTTP transport, without API
calls or a spaCy model download.

API references: [structured outputs](https://aistudio.google.com/docs/structured-output),
[text generation](https://aistudio.google.com/docs/text-generation), and
[supported API interfaces](https://aistudio.google.com/docs/interactions).
