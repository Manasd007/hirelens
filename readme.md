# HireLens

**Intelligent Resume Screening & Interview Scheduling Platform**

HireLens is an AI-powered tool that helps hiring teams **screen resumes, shortlist top candidates, and schedule interviews** — all in one place.
Instead of relying on keyword matching, it uses **semantic similarity and language understanding** to find the best fits for a role.

---

## 🚀 Features

### 1. **Smart Resume Scoring**

* Upload a job description and candidate resumes (PDF/DOCX).
* Scores each resume **0–100** based on semantic role fit.
* Provides a detailed reasoning log for transparency.
* Identifies matched and missing skills automatically.

### 2. **Shortlisting**

* Selects **top N candidates** (configurable).
* Explains why each candidate was shortlisted.
* Supports **instant re-ranking** if the job description changes.

### 3. **Google Meet Scheduling**

* Connects with **Google Calendar API**.
* Finds available slots for interviewers and candidates.
* Sends invites automatically.
* Detects time zone differences and prevents conflicts.
* Supports auto-rescheduling.

### 4. **Learning from Feedback**

* Improves scoring when hiring managers label candidates as a “good fit” or “poor fit.”
* Supports **offline** (simulated) and **online** (manual) reinforcement learning.

---

## 🗂 Folder Structure

```
HireLens/
│── api/                # FastAPI backend
│── services/           # Core business logic (parser, scorer, scheduler, etc.)
│── streamlit/           # Frontend UI
│── data/
│   ├── jd/             # Job descriptions
│   ├── resumes/        # Uploaded resumes
│   ├── outputs/        # Processed results
│── requirements.txt     # Python dependencies
│── README.md
│── .gitignore
```

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Frontend**: Streamlit (with animations & charts)
* **AI / NLP**: Sentence Transformers, FAISS
* **Scheduling**: Google Calendar API
* **File Parsing**: PyMuPDF, python-docx
* **Database**: JSON-based storage (extensible to PostgreSQL)
* **Deployment**: Docker-ready

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Manasd007/hirelens.git
cd hirelens
```

### 2. Create Data Directories

```bash
mkdir -p data/{resumes,jd,outputs}
touch data/resumes/.gitkeep data/jd/.gitkeep data/outputs/.gitkeep
```

### 3. Create Virtual Environment & Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

pip install -r requirements.txt
```

### 4. Setup Google Calendar API

* Go to **[Google Cloud Console](https://console.cloud.google.com/)**
* Create a project → Enable Google Calendar API
* Configure **OAuth consent screen**
* Add redirect URI:

  ```
  http://localhost:8000/auth/callback
  ```
* Download `credentials.json` and place it in the project root.

### 5. Run Backend

```bash
uvicorn api.main:app --reload
```

### 6. Run Frontend

```bash
streamlit run streamlit/streamlit_app.py
```

---

## 🖥 Usage

1. **Upload a Job Description** – Paste text or upload a JD file.
2. **Upload Candidate Resumes** – PDF/DOCX, multiple at once.
3. **View AI Scores** – See 0–100 match scores and reasoning logs.
4. **Shortlist Candidates** – Pick top N and refine instantly.
5. **Schedule Interviews** – Connect Google Calendar and send invites.

---

## 📊 Example Output

**Resume Scoring:**

```
Manas_Dubey_Resume – Score: 68.6
Matched Skills: api, docker, faiss, fastapi, ml, nlp, python, transformers
Gaps: google calendar, oauth, scheduling
```

**Shortlist (Top 2 Candidates):**

```
1. Manas Dubey – 68.6
2. Jane Smith – 64.2
```

---



## 🤝 Contributing

1. Fork the repo
2. Create a new branch: `feature/your-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push and open a pull request

---

## 📜 License

MIT License — feel free to use and modify.

-
