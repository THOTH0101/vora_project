from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CandidateModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(CandidateModel):
    quote: str = Field(min_length=1, description="Exact quotation from the redacted CV.")
    page: int | None = Field(
        default=None, ge=1, description="Enclosing [PAGE N] marker, if supplied."
    )
    confidence: float | None = Field(default=None, ge=0, le=1)


class ProfessionalIdentity(CandidateModel):
    primary_group: Literal[
        "medical",
        "nursing",
        "allied_health",
        "pharmacy",
        "medical_laboratory",
        "healthcare_administration",
        "other",
        "unknown",
    ] = "unknown"

    primary_profession: str | None = None
    additional_professions: list[str] = Field(default_factory=list)
    professional_titles: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class CandidateLocation(CandidateModel):
    nationality: str | None = None
    current_country_of_residence: str | None = None
    state_or_region: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class LicenseClaim(CandidateModel):
    profession: str | None = None
    regulator: str | None = None
    licence_number: str | None = None
    country_code: str | None = None
    jurisdiction: str | None = None

    registration_type: str | None = None
    status_claimed: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)


class LanguageRecord(CandidateModel):
    language: str = Field(min_length=1)
    proficiency: str | None = None
    proficiency_framework: str | None = None
    certificate: str | None = None
    score: str | None = None
    test_date: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class ExaminationRecord(CandidateModel):
    name: str = Field(min_length=1)
    category: Literal[
        "language",
        "medical_licensing",
        "professional",
        "migration",
        "other",
    ]

    destination_country: str | None = None
    stage: str | None = None
    result: str | None = None
    score: str | None = None
    examination_date: str | None = None
    expiry_date: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)


class EducationRecord(CandidateModel):
    qualification: str = Field(min_length=1)
    education_level: str | None = None
    field_of_study: str | None = None
    institution: str | None = None
    country: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class EmploymentRecord(CandidateModel):
    role: str = Field(min_length=1)
    employer: str | None = None

    start_date: str | None = None
    end_date: str | None = None
    date_precision: Literal["day", "month", "year", "unknown"] = "unknown"

    is_current: bool | None = None

    work_functions: list[str] = Field(default_factory=list)
    practice_settings: list[str] = Field(default_factory=list)

    specialty: str | None = None
    institution_type: str | None = None
    institution_ownership: str | None = None
    institution_care_level: str | None = None

    evidence: list[Evidence] = Field(default_factory=list)


class SpecialtyRecord(CandidateModel):
    name: str = Field(min_length=1)
    subspecialty: str | None = None
    qualification: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class SkillRecord(CandidateModel):
    name: str = Field(min_length=1)
    category: str | None = None
    proficiency: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class ExperienceSummary(CandidateModel):
    total_months: int | None = None
    clinical_months: int | None = None
    administrative_months: int | None = None
    academic_months: int | None = None
    research_months: int | None = None
    laboratory_months: int | None = None
    specialty_months: dict[str, int] = Field(default_factory=dict)


class CandidateProfile(CandidateModel):
    schema_version: Literal["1.0"] = "1.0"

    identity: ProfessionalIdentity
    location: CandidateLocation

    licences: list[LicenseClaim] = Field(default_factory=list)
    languages: list[LanguageRecord] = Field(default_factory=list)
    examinations: list[ExaminationRecord] = Field(default_factory=list)
    education: list[EducationRecord] = Field(default_factory=list)

    employment_history: list[EmploymentRecord] = Field(default_factory=list)

    specialties: list[SpecialtyRecord] = Field(default_factory=list)
    skills: list[SkillRecord] = Field(default_factory=list)

    experience: ExperienceSummary = Field(default_factory=ExperienceSummary)
