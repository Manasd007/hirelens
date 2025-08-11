
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from typing import List

from hirelens.configs.settings import settings
from hirelens.models.schema import (
    JobDescription, CandidateScore, ScoreBreakdown,
    ShortlistRequest, ScheduleRequest, FeedbackBatch,
    ShortlistPayload,
)
from hirelens.services import parser, scorer, shortlist, scheduler
from hirelens.learning.feedback import update_weights

app = FastAPI(title="HireLens", version="0.1.0")
print("[main] loaded:", __file__)
@app.post("/shortlist", response_model=List[CandidateScore])

def shortlist_top(payload: ShortlistPayload):
    return shortlist.shortlist(payload.scores, payload.top_n)

@app.get("/health")
def health():
    return {"ok": True}

@app.on_event("startup")
def _startup():
    try:
        from hirelens.api.deps import warm_models
        warm_models()
    except Exception as e:
        print(f"[startup] warm_models failed: {e}")

@app.post("/ingest/score", response_model=List[CandidateScore])
def ingest_and_score(jd: JobDescription):
    resumes = parser.load_resumes(settings.RESUME_DIR)
    weights = {
        "skills": settings.WEIGHT_SKILLS,
        "experience": settings.WEIGHT_EXPERIENCE,
        "education": settings.WEIGHT_EDUCATION,
        "seniority": settings.WEIGHT_SENIORITY,
    }
    out: List[CandidateScore] = []
    for r in resumes:
        final, br = scorer.score_candidate(jd.text, r["text"], weights)
        jd_sk = scorer.extract_skills(jd.text)
        cv_sk = scorer.extract_skills(r["text"])
        gaps = shortlist.skills_gap(jd.text, r["text"])
        reasoning = (
            f"{r['name']} – semantic fit {final:.1f}. "
            f"Matched skills: {', '.join(sorted(set(jd_sk) & set(cv_sk))) or '—'}. "
            f"Gaps: {', '.join(gaps) or '—'}. "
            f"Breakdown(skills={br['skills']:.1f}, exp={br['experience']:.1f}, "
            f"edu={br['education']:.1f}, seniority={br['seniority']:.1f})."
        )
        out.append(CandidateScore(
            resume_id=r["id"],
            name=r["name"],
            score=round(final, 1),
            breakdown=ScoreBreakdown(**br),
            reasoning=reasoning,
        ))
    return sorted(out, key=lambda x: x.score, reverse=True)

@app.post("/shortlist", response_model=List[CandidateScore])
def shortlist_top(scores: List[CandidateScore], req: ShortlistRequest):
    return shortlist.shortlist(scores, req.top_n)

@app.post("/schedule")
def schedule(req: ScheduleRequest):
    out = scheduler.schedule_meet(
        interviewer_email=req.interviewer_email,
        candidate_email=req.candidate_email,
        start_iso=req.window_start_iso,
        end_iso=req.window_end_iso,
        title=req.title,
        description=req.description,
        timezone=req.timezone,
    )
    return JSONResponse(out)

@app.post("/feedback/update-weights")
def feedback_update(batch: FeedbackBatch):
    current = {
        "skills": settings.WEIGHT_SKILLS,
        "experience": settings.WEIGHT_EXPERIENCE,
        "education": settings.WEIGHT_EDUCATION,
        "seniority": settings.WEIGHT_SENIORITY,
    }
    fb = [f.model_dump() for f in batch.feedback]
    new_w = update_weights(fb, current)
    return JSONResponse({"old": current, "new": new_w})


@app.get("/")
def root():
    return RedirectResponse(url="/docs")
