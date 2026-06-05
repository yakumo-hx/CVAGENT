from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


EvidenceStatus = Literal["DIRECT", "TRANSFERABLE", "ADJACENT", "WEAK", "GAP"]
Confidence = Literal["low", "medium", "high"]


class Metric(BaseModel):
    type: str = ""
    value: str | None = None
    status: Literal["provided", "missing", "estimated"] = "missing"


class ResumeItem(BaseModel):
    id: str
    title: str = ""
    organization: str = ""
    role: str = ""
    period: str = ""
    description: str = ""
    tools: list[str] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class MasterResume(BaseModel):
    profile: dict[str, str] = Field(default_factory=dict)
    education: list[ResumeItem] = Field(default_factory=list)
    experiences: list[ResumeItem] = Field(default_factory=list)
    projects: list[ResumeItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certificates: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    raw_text: str = ""


class JDRequirement(BaseModel):
    id: str
    text: str
    category: Literal["must_have", "nice_to_have", "responsibility", "hidden"]
    keywords: list[str] = Field(default_factory=list)
    evidence_needed: list[str] = Field(default_factory=list)


class JDAnalysis(BaseModel):
    job_title: str = ""
    company: str = ""
    seniority: str = ""
    must_have_requirements: list[JDRequirement] = Field(default_factory=list)
    nice_to_have_requirements: list[JDRequirement] = Field(default_factory=list)
    responsibilities: list[JDRequirement] = Field(default_factory=list)
    hidden_expectations: list[JDRequirement] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    business_context: str = ""
    interview_risks: list[str] = Field(default_factory=list)


class MatchScore(BaseModel):
    direct: int = Field(ge=0, le=100)
    transferable: int = Field(ge=0, le=100)
    adjacent: int = Field(ge=0, le=100)
    impact: int = Field(ge=0, le=100)
    total: int = Field(ge=0, le=100)
    status: EvidenceStatus


class MatrixRow(BaseModel):
    requirement_id: str
    requirement_text: str
    best_evidence_id: str | None = None
    best_evidence_summary: str = ""
    score: MatchScore
    gap: str = ""
    next_question: str = ""


class FactCard(BaseModel):
    fact_id: str
    claim: str
    source: Literal["user_answer", "resume", "sample_data"] = "user_answer"
    related_jd_requirements: list[str] = Field(default_factory=list)
    related_experience: str = ""
    tools: list[str] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    role: str = ""
    outcome: str = ""
    confidence: Confidence = "medium"
    risk: str = ""
    can_use_in_resume: bool = False
    needs_confirmation: bool = True

    @field_validator("claim")
    @classmethod
    def claim_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("fact claim cannot be empty")
        return value.strip()


class ResumeBullet(BaseModel):
    variant: Literal["conservative", "standard", "jd_strong", "placeholder"]
    text: str
    fact_ids: list[str]
    related_jd_requirements: list[str] = Field(default_factory=list)
    risk: str = ""
    gap_suggestions: list[str] = Field(default_factory=list)


class RiskFinding(BaseModel):
    code: str
    message: str
    severity: Literal["low", "medium", "high"] = "medium"


class ExportBundle(BaseModel):
    tailored_resume_md: str = ""
    evidence_cards_json: str = ""
    jd_analysis_json: str = ""
    gap_report_md: str = ""
    interview_prep_md: str = ""
