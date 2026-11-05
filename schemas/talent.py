from typing import Optional
from pydantic import BaseModel, Field


class Nationality(BaseModel):
    country: str


class License(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class Language(BaseModel):
    name: str
    level: str


class Examination(BaseModel):
    name: str
    examining_body: Optional[str] = None
    subjects: list[str] = Field(default_factory=list)
    grades: list[str] = Field(default_factory=list)
    examination_date: Optional[str] = None


class Education(BaseModel):
    qualification: str
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    institution_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class Experience(BaseModel):
    job_title: str
    company: Optional[str] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    level: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    role: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    name: str
    level: str
    is_specialty: bool = False


class Candidate(BaseModel):
    nationality: list[Nationality] = Field(default_factory=list)
    language: list[Language] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    license: list[License] = Field(default_factory=list)
    examinations: list[Examination] = Field(default_factory=list)

    residence: str
    highest_education_level: Optional[str] = None
    total_experience_months: Optional[int] = None
    experience_level: Optional[str] = None
