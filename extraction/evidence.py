from privacy.entity_hints import PAGE_MARKER_RE, REDACTION_MARKER_RE
from schemas.candidate import CandidateProfile, ExperienceSummary


def _contains_redacted_value(value) -> bool:
    if isinstance(value, str):
        return bool(REDACTION_MARKER_RE.search(value))
    if isinstance(value, list):
        return any(_contains_redacted_value(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_redacted_value(item) for item in value.values())
    return False


def validate_profile_evidence(profile: CandidateProfile, cv_text: str) -> None:
    """Check quoted evidence, page provenance, and extraction-only fields."""
    if profile.experience != ExperienceSummary():
        raise ValueError("experience summaries must remain empty")

    markers = list(PAGE_MARKER_RE.finditer(cv_text))
    pages = {}
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(cv_text)
        pages[int(marker[1])] = cv_text[marker.end() : end]

    for section_name, section in profile:
        records = section if isinstance(section, list) else [section]
        for index, record in enumerate(records):
            if not hasattr(record, "evidence"):
                continue
            path = f"{section_name}[{index}]" if isinstance(section, list) else section_name
            values = record.model_dump(exclude={"evidence"})
            group = values.pop("primary_group", "unknown")
            populated = group != "unknown" or any(
                value not in (None, "", [], {}, "unknown") for value in values.values()
            )
            if not populated and isinstance(section, list):
                raise ValueError(f"{path} has no supported fields")
            if (populated or isinstance(section, list)) and not record.evidence:
                raise ValueError(f"{path} requires evidence")
            if _contains_redacted_value(values):
                raise ValueError(f"{path} contains a redacted value outside evidence")
            for evidence in record.evidence:
                if not evidence.quote.strip() or evidence.quote not in cv_text:
                    raise ValueError(f"{path} quote is absent from the redacted CV")
                if pages:
                    if evidence.page not in pages:
                        raise ValueError(f"{path} requires a valid source page")
                    if evidence.quote not in pages[evidence.page]:
                        raise ValueError(f"{path} quote does not occur on its source page")
                elif evidence.page is not None:
                    raise ValueError(f"{path} page cannot be determined without page markers")
