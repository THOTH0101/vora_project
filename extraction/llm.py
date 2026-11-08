import json
from functools import lru_cache

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from config import GEMINI_API_KEY, GEMINI_MODEL
from extraction.evidence import validate_profile_evidence
from extraction.prompt import DOMAIN_GUIDANCE, SYSTEM_INSTRUCTION
from privacy.entity_hints import sanitize_entity_hints
from schemas.candidate import CandidateProfile


class GeminiExtractionError(RuntimeError):
    """Gemini could not produce a complete, validated candidate profile."""


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    if not GEMINI_API_KEY or not GEMINI_API_KEY.strip():
        raise GeminiExtractionError("Set GEMINI_API_KEY in the environment or .env")

    return genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=60_000),
    )


def extract_candidate_profile(
    cv_text: str,
    professional_group: str = "unknown",
    *,
    entities: list[dict] | None = None,
) -> CandidateProfile:
    """Extract from PII-redacted text and optional privacy-filtered spaCy hints."""
    if not cv_text or not cv_text.strip():
        raise ValueError("CV text cannot be empty")

    domain_instruction = DOMAIN_GUIDANCE.get(
        professional_group, DOMAIN_GUIDANCE["unknown"]
    )
    system_instruction = (
        f"{SYSTEM_INSTRUCTION}\n\nPROFESSIONAL DOMAIN GUIDANCE:\n{domain_instruction}"
    )
    # JSON encoding keeps CV contents and entity hints in explicit data fields.
    # Never include the original text or Presidio's recovered PII here.
    contents = json.dumps(
        {
            "redacted_cv_text": cv_text,
            "entity_hints": sanitize_entity_hints(entities or [], cv_text),
        },
        ensure_ascii=False,
    )

    try:
        response = get_gemini_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_json_schema=CandidateProfile.model_json_schema(),
                max_output_tokens=12000,
            ),
        )
    except GeminiExtractionError:
        raise
    except errors.APIError as exc:
        raise GeminiExtractionError(
            f"Gemini candidate extraction request failed (HTTP {exc.code})"
        ) from exc
    except Exception as exc:
        raise GeminiExtractionError("Gemini candidate extraction request failed") from exc

    if response.prompt_feedback and response.prompt_feedback.block_reason:
        raise GeminiExtractionError("Gemini blocked the candidate extraction request")

    if not response.candidates:
        raise GeminiExtractionError("Gemini returned an empty response")

    finish_reason = response.candidates[0].finish_reason
    if finish_reason != types.FinishReason.STOP:
        reason = finish_reason.value if finish_reason else "unknown"
        raise GeminiExtractionError(f"Gemini returned an incomplete response ({reason})")

    if not response.text or not response.text.strip():
        raise GeminiExtractionError("Gemini returned an empty response")

    try:
        profile = CandidateProfile.model_validate_json(response.text)
    except ValidationError as exc:
        raise GeminiExtractionError(
            "Gemini response does not match the candidate schema"
        ) from exc

    try:
        validate_profile_evidence(profile, cv_text)
    except ValueError as exc:
        raise GeminiExtractionError(
            f"Gemini profile failed evidence validation: {exc}"
        ) from exc

    return profile
