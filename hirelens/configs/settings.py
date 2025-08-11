# hirelens/configs/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict  # <- v2 package


class Settings(BaseSettings):
    # v2 config style
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # -------------------------------
    # Model & Data paths
    # -------------------------------
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # project root
    DATA_DIR: Path = BASE_DIR / "data"

    # If your resumes really live in data/jd/resumes/outputs, keep this.
    # Otherwise change to: DATA_DIR / "resumes"
    RESUME_DIR: Path = DATA_DIR / "resumes"
    JD_DIR: Path = DATA_DIR / "jd"
    OUTPUT_DIR: Path = DATA_DIR / "outputs"
    INDEX_PATH: Path = OUTPUT_DIR / "faiss.index"

    # -------------------------------
    # Google Calendar API
    # -------------------------------
    GOOGLE_OAUTH_CREDS: Path = BASE_DIR / "google_oauth_credentials.json"
    GOOGLE_CALENDAR_ID: str = "primary"
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"

    # -------------------------------
    # Initial scoring weights
    # -------------------------------
    WEIGHT_SKILLS: float = 0.45
    WEIGHT_EXPERIENCE: float = 0.35
    WEIGHT_EDUCATION: float = 0.10
    WEIGHT_SENIORITY: float = 0.10


# Instantiate settings
settings = Settings()

# Ensure required directories exist
for path in [settings.DATA_DIR, settings.RESUME_DIR, settings.JD_DIR, settings.OUTPUT_DIR]:
    Path(path).mkdir(parents=True, exist_ok=True)
