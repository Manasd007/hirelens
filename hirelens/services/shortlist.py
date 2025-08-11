# hirelens/services/shortlist.py
from typing import List
from hirelens.models.schema import CandidateScore
from hirelens.services.scorer import extract_skills

def shortlist(candidates: List[CandidateScore], top_n: int) -> List[CandidateScore]:
    return sorted(candidates, key=lambda c: c.score, reverse=True)[:top_n]

def skills_gap(jd_text: str, cv_text: str) -> List[str]:
    jd = set(extract_skills(jd_text))
    cv = set(extract_skills(cv_text))
    return sorted(list(jd - cv))
