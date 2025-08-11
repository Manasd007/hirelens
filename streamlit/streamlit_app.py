import os
import json
import time
import datetime as dt
from pathlib import Path
from typing import List, Dict, Any
from typing import Optional
import requests
import pandas as pd
import streamlit as st
from streamlit_lottie import st_lottie

API_DEFAULT = "http://127.0.0.1:8000"
DATA_DIR = Path("data")
RESUME_DIR = DATA_DIR / "resumes"
JD_FILE = DATA_DIR / "jd" / "jd.txt"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
JD_FILE.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="HireLens",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
:root {
  --bg: #0b1220;
  --panel: rgba(255, 255, 255, 0.04);
  --border: rgba(255, 255, 255, 0.08);
  --text: #e6ebff;
  --muted: #b5c0ff;
  --primary: #7c9dff;
  --success: #22c55e;
  --warning: #eab308;
  --danger: #ef4444;
}
html, body, [class*="css"]  {font-family: Inter, Segoe UI, system-ui, -apple-system, Roboto, Arial, sans-serif;}
/* full-bleed gradient header */
.hero {
  border-radius: 18px;
  padding: 18px 22px;
  background: radial-gradient(1200px 500px at right -20% top -30%, rgba(124,157,255,.22), transparent 55%),
              radial-gradient(900px 400px at left -10% bottom -40%, rgba(34,197,94,.18), transparent 50%),
              linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
  border: 1px solid var(--border);
  color: var(--text);
}
.subtle { color: var(--muted); }
.card {
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--panel);
  padding: 16px 18px;
  backdrop-filter: blur(8px);
}
.kpi {
  display:flex; align-items:center; gap:.6rem;
  background: linear-gradient(180deg, rgba(124,157,255,.12), rgba(124,157,255,.04));
  border: 1px solid rgba(124,157,255,.25);
  padding: 8px 10px; border-radius: 12px; font-weight:600;
}
.badge {
  display:inline-block; padding:2px 8px; border-radius:999px;
  font-size:12px; border:1px solid var(--border); color:var(--muted);
}
.score-pill {
  display:inline-block; padding:5px 12px; border-radius:999px;
  background: rgba(34,197,94,.15); color:#22c55e; border:1px solid rgba(34,197,94,.3);
  font-weight:700;
}
.small { font-size: 12px; opacity: .8; }
hr { border: none; border-top: 1px solid var(--border); margin: 14px 0 18px; }
footer { visibility: hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.sidebar.title("⚙️ Settings")
api_base = st.sidebar.text_input("FastAPI server", value=API_DEFAULT, help="Your HireLens API base URL")
st.sidebar.caption(f"📁 Resume folder: {RESUME_DIR.resolve()}")
clear = st.sidebar.button("🧹 Clear uploaded resumes")
if clear:
    for p in RESUME_DIR.glob("*"):
        try: p.unlink()
        except: pass
    st.sidebar.success("Cleared resumes folder.")

@st.cache_data(show_spinner=False)
def load_lottie(url: str) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

LOTTIE_HERO = load_lottie("https://assets7.lottiefiles.com/packages/lf20_V9t630.json")          # dev desk
LOTTIE_OK = load_lottie("https://assets3.lottiefiles.com/packages/lf20_s1hjbpsc.json")           # check
LOTTIE_SCAN = load_lottie("https://assets3.lottiefiles.com/packages/lf20_9wpyhdzo.json")         # scan
LOTTIE_THINK = load_lottie("https://assets6.lottiefiles.com/packages/lf20_kyu7xb1v.json")        # brain swirl

c1, c2 = st.columns([0.64, 0.36], vertical_alignment="center")
with c1:
    st.markdown(
        """
        <div class="hero">
          <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
             <div class="kpi">HireLens</div>
             <span class="badge">Semantic Scoring</span>
             <span class="badge">Shortlist</span>
             <span class="badge">Feedback</span>
             <span class="badge">Scheduling</span>
          </div>
          <div style="margin-top:10px; font-size:15px;" class="subtle">
            Upload resumes, paste JD, get explainable scores. Refine with feedback. Optionally schedule Google Meet—all in one place.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    if LOTTIE_HERO:
        st_lottie(LOTTIE_HERO, height=180, key="hero")

st.write("")

tab1, tab2, tab3 = st.tabs(["🏗️ Score & Shortlist", "📝 Feedback", "📅 Scheduling"])


with tab1:
    left, right = st.columns([0.58, 0.42])

    with left:
        st.subheader("1) Job Description")
        jd_text = st.text_area(
            "Paste the JD",
            value=(JD_FILE.read_text(encoding="utf-8") if JD_FILE.exists() else ""),
            height=180,
            placeholder="Paste a descriptive JD here (not just keywords)…",
        )
        if st.button("💾 Save JD"):
            JD_FILE.write_text(jd_text, encoding="utf-8")
            st.success("Saved JD to data/jd/jd.txt")
            if LOTTIE_OK: st_lottie(LOTTIE_OK, height=90, key="saved-jd")

    with right:
        st.subheader("2) Resumes")
        up = st.file_uploader(
            "Upload PDFs / DOCX / TXT (stored in data/resumes)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )
        if up:
            for f in up:
                (RESUME_DIR / f.name).write_bytes(f.read())
            st.success(f"Uploaded {len(up)} file(s).")
        with st.expander("Files in folder", expanded=False):
            items = [p.name for p in RESUME_DIR.glob("*") if p.is_file()]
            st.write(items if items else "— none —")

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.subheader("3) Run Scoring")
    colA, colB = st.columns([0.22, 0.78])
    top_n = colA.slider("Shortlist top N", 1, 10, 3)
    run_now = colA.button("🚀 Score & Shortlist", type="primary", use_container_width=True)

    if run_now:
        if not jd_text.strip():
            st.error("Please paste the JD first.")
        else:
            with st.spinner("Scoring resumes… first time may take ~30–60s to download the embedding model"):
                if LOTTIE_SCAN:
                    st_lottie(LOTTIE_SCAN, height=120, key="scan")

                try:
                    r = requests.post(
                        f"{api_base}/ingest/score",
                        json={"id": "jd-ui", "title": "UI JD", "text": jd_text},
                        timeout=300
                    )
                    r.raise_for_status()
                    scores = r.json()
                except Exception as e:
                    st.error(f"Error calling /ingest/score: {e}")
                    scores = []

            if scores:
                try:
                    r2 = requests.post(
                        f"{api_base}/shortlist",
                        json={"scores": scores, "top_n": top_n},
                        timeout=60
                    )
                    r2.raise_for_status()
                    top = r2.json()
                except Exception as e:
                    st.warning(f"Could not call /shortlist: {e}. Showing the top {top_n} locally.")
                    top = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_n]

                st.markdown("##### All candidates")
                df = pd.DataFrame(scores)
                st.dataframe(df[["name", "score", "reasoning"]], hide_index=True, use_container_width=True)

                st.markdown("##### Shortlist")
                for c in top:
                    with st.container(border=True):
                        st.markdown(
                            f"**{c['name']}** &nbsp; "
                            f"<span class='score-pill'>Score {c['score']}</span>",
                            unsafe_allow_html=True
                        )
                        b = c["breakdown"]
                        st.progress(min(int(c["score"]), 100), text=f"Overall: {c['score']}")
                        cols = st.columns(4)
                        cols[0].metric("Skills", f"{b['skills']:.1f}")
                        cols[1].metric("Experience", f"{b['experience']:.1f}")
                        cols[2].metric("Education", f"{b['education']:.1f}")
                        cols[3].metric("Seniority", f"{b['seniority']:.1f}")
                        st.caption(c["reasoning"])
                st.balloons()
            else:
                st.warning("No scores returned. Ensure resumes exist in data/resumes and the JD is not empty.")

with tab2:
    st.subheader("Lightweight Learning — nudge weights with feedback")
    st.caption("Mark candidates as good/poor fit. Weights update slightly; re-run scoring to see changes.")

    col1, col2 = st.columns(2)
    gf = col1.text_input("👍 Good fit resume_id(s), comma-separated", placeholder="resume.pdf")
    pf = col2.text_input("👎 Poor fit resume_id(s), comma-separated", placeholder="resume 3.pdf")

    if st.button("Update Weights", type="secondary"):
        items = []
        for x in [s.strip() for s in gf.split(",") if s.strip()]:
            items.append({"resume_id": x, "label": "good_fit"})
        for x in [s.strip() for s in pf.split(",") if s.strip()]:
            items.append({"resume_id": x, "label": "poor_fit"})
        if not items:
            st.info("No feedback provided.")
        else:
            try:
                r = requests.post(f"{api_base}/feedback/update-weights", json={"feedback": items}, timeout=60)
                r.raise_for_status()
                st.success("Weights updated")
                if LOTTIE_THINK: st_lottie(LOTTIE_THINK, height=120, key="learn")
                st.json(r.json())
            except Exception as e:
                st.error(f"Error calling /feedback/update-weights: {e}")

with tab3:
    st.subheader("Create a Google Meet invite")
    st.caption("Requires Google Calendar OAuth set on the backend. First call will ask for consent in a browser window.")

    colA, colB = st.columns(2)
    interviewer = colA.text_input("Interviewer email", value="")
    candidate = colB.text_input("Candidate email", value="")
    title = st.text_input("Title", value="HireLens Interview")
    desc = st.text_area("Description", value="Introductory call")
    tz = st.text_input("Timezone", value="Asia/Kolkata")

    day = st.date_input("Date", value=dt.date.today())
    c1, c2 = st.columns(2)
    t_start = c1.time_input("Start time", value=dt.time(11, 0))
    t_end   = c2.time_input("End time", value=dt.time(11, 30))

    start_iso = dt.datetime.combine(day, t_start).isoformat(timespec="seconds")
    end_iso   = dt.datetime.combine(day, t_end).isoformat(timespec="seconds")

    if st.button("Create Google Meet invite", type="primary"):
        if not (interviewer and candidate):
            st.error("Please fill both emails.")
        elif end_iso <= start_iso:
            st.error("End time must be after start time.")
        else:
            with st.spinner("Creating event…"):
                try:
                    r = requests.post(
                        f"{api_base}/schedule",
                        json={
                            "interviewer_email": interviewer,
                            "candidate_email": candidate,
                            "duration_minutes": int((dt.datetime.fromisoformat(end_iso) - dt.datetime.fromisoformat(start_iso)).total_seconds() // 60),
                            "window_start_iso": start_iso,
                            "window_end_iso": end_iso,
                            "title": title,
                            "description": desc,
                            "timezone": tz
                        },
                        timeout=120
                    )
                    r.raise_for_status()
                    st.success("Event created")
                    if LOTTIE_OK: st_lottie(LOTTIE_OK, height=100, key="event-ok")
                    st.json(r.json())
                except requests.HTTPError:
                    try:
                        st.error(r.json())
                    except Exception:
                        st.error("Server returned an error (see backend logs).")
                except Exception as e:
                    st.error(f"Error calling /schedule: {e}")

st.markdown("<div class='small'>© HireLens — demo UI</div>", unsafe_allow_html=True)
