from typing import Dict, List


def _renormalize(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def update_weights(feedback_items: List[dict], current_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Very light bandit-style updater:
      - 'good_fit'  => nudge skills & experience up a bit
      - 'poor_fit'  => nudge skills & experience down a bit
    Then renormalize so weights sum to 1.0.

    feedback_items: List of dicts with keys:
        - resume_id: str
        - label: 'good_fit' | 'poor_fit'
        - notes: Optional[str]
    current_weights: dict with keys 'skills', 'experience', 'education', 'seniority'
    """
    w = dict(current_weights)

    MIN_W, MAX_W = 0.1, 0.6
    STEP = 0.02 

    for fb in feedback_items or []:
        label = (fb.get("label") or "").strip().lower()
        if label == "good_fit":
            w["skills"] = min(w.get("skills", 0.0) + STEP, MAX_W)
            w["experience"] = min(w.get("experience", 0.0) + STEP, MAX_W)
        elif label == "poor_fit":
            w["skills"] = max(w.get("skills", 0.0) - STEP, MIN_W)
            w["experience"] = max(w.get("experience", 0.0) - STEP, MIN_W)
     
    w = _renormalize(w)
    return w
