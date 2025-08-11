# hirelens/services/scorer.py
import re
import numpy as np
from typing import Dict, List, Tuple
from hirelens.services.embeddings import embed_texts
from hirelens.configs.settings import settings

SEED_SKILLS = [
    "python","fastapi","node","react","docker","kubernetes","nlp","embeddings","faiss",
    "pandas","sql","gcp","aws","oauth","google calendar","scheduling","etl","api",
    "vector db","langchain","ml","classification","regression","transformers"
]

def extract_skills(text: str) -> List[str]:
    t = (text or "").lower()
    return [s for s in SEED_SKILLS if s in t]

def estimate_experience_years(text: str) -> float:
    yrs = [int(x) for x in re.findall(r"(\d+)\s+year", (text or "").lower())]
    return float(max(yrs) if yrs else 0)

def score_candidate(jd_text: str, resume_text: str, weights: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    embs = embed_texts([jd_text, resume_text], settings.EMBEDDING_MODEL)
    sim = float(np.dot(embs[0], embs[1]))  # 0..1

    jd_skills = set(extract_skills(jd_text))
    cv_skills = set(extract_skills(resume_text))
    skill_overlap = len(jd_skills & cv_skills) / (len(jd_skills) or 1)

    jd_years = estimate_experience_years(jd_text)
    cv_years = estimate_experience_years(resume_text)
    exp_score = min(cv_years / (jd_years or 1), 1.0)

    edu_score = 0.7 if any(k in (resume_text or "").lower() for k in ["b.tech","btech","b.e","be ","mtech","m.tech","masters","m.sc","mca"]) else 0.4
    seniority_score = 0.5 + 0.5 * sim

    total = (
        weights["skills"] * skill_overlap +
        weights["experience"] * exp_score +
        weights["education"] * edu_score +
        weights["seniority"] * seniority_score
    )
    final = (0.6 * (total * 100.0)) + (0.4 * (sim * 100.0))
    breakdown = {
        "skills": skill_overlap * 100.0,
        "experience": exp_score * 100.0,
        "education": edu_score * 100.0,
        "seniority": seniority_score * 100.0
    }
    return final, breakdown
