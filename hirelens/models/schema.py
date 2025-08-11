# hirelens/models/schema.py
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import BaseModel, Field

class ResumeItem(BaseModel):
    id: str
    name: str
    path: str
    text: str


class JobDescription(BaseModel):
    id: str
    title: str
    text: str
    must_have: List[str] = Field(default_factory=list)
    nice_to_have: List[str] = Field(default_factory=list)
    min_years: Optional[int] = None


class ScoreBreakdown(BaseModel):
    skills: float
    experience: float
    education: float
    seniority: float


class CandidateScore(BaseModel):
    resume_id: str
    name: str
    score: float  # 0–100
    breakdown: ScoreBreakdown
    reasoning: str


class ShortlistRequest(BaseModel):
    top_n: int = 5

class ShortlistPayload(BaseModel):
    scores: List[CandidateScore]
    top_n: int = 5
class ScheduleRequest(BaseModel):
    interviewer_email: str
    candidate_email: str
    duration_minutes: int = 30
    window_start_iso: str  # e.g. "2025-08-11T11:00:00"
    window_end_iso: str    # e.g. "2025-08-11T11:30:00"
    title: str
    description: Optional[str] = None
    timezone: str = "Asia/Kolkata"


class FeedbackItem(BaseModel):
    resume_id: str
    label: str  # "good_fit" | "poor_fit"
    notes: Optional[str] = None


class FeedbackBatch(BaseModel):
    feedback: List[FeedbackItem]
