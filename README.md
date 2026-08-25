# AI Resume Analyzer

Flask + MySQL + HTML app that scores a resume against a job description
(TF-IDF / cosine similarity) and highlights matched vs. missing skills.

## Project structure
```
ai-resume-analyzer/
├── app.py                 # Flask backend + analysis logic
├── schema.sql              # MySQL database schema
├── index.html              # Web Interface UI + Privacy Modal
├── PRIVACY_POLICY.md       # Application Privacy & Data Policy
├── .gitignore              # Ignored files and folders
└── requirements.txt
```

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create the database**
   ```bash
   mysql -u root -p < schema.sql
   ```

3. **Set DB credentials** (env vars, defaults shown)
   ```bash
   export DB_HOST=localhost
   export DB_USER=root
   export DB_PASSWORD=yourpassword
   export DB_NAME=resume_analyzer
   ```

4. **Run the app**
   ```bash
   python app.py
   ```
   Open http://localhost:5000

## How scoring works
- Resume text is extracted from PDF/DOCX/TXT.
- Resume + job description are vectorized with TF-IDF and compared via
  cosine similarity → a 0–100 match score.
- A built-in skills dictionary (`SKILL_KEYWORDS` in `app.py`) is scanned
  in both texts to report **matched** and **missing** skills.
- Every analysis is saved to MySQL (`resumes`, `job_descriptions`,
  `analysis_results` tables) if the DB is reachable; the UI still shows
  results even if it isn't.

## Privacy & Security
For detailed information regarding how resume data is collected, stored locally, and processed safely, see [PRIVACY_POLICY.md](file:///c:/Users/Sanjay%20G%20L/Desktop/AI%20Resume%20Analyzer/PRIVACY_POLICY.md).

## Customizing
- Add more terms to `SKILL_KEYWORDS` in `app.py` for your domain.
- Swap TF-IDF for embeddings (e.g., sentence-transformers) for smarter
  semantic matching if you want a heavier ML dependency.

