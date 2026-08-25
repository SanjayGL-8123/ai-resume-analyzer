"""
AI Resume Analyzer - Flask backend
-----------------------------------
Upload a resume (PDF/DOCX), paste a job description, and get:
  - a match score (TF-IDF + cosine similarity)
  - matched / missing skills
  - results stored in MySQL

Run:
    pip install -r requirements.txt
    python app.py
"""

import os
import re
import io

from flask import Flask, request, render_template, jsonify
import mysql.connector
from mysql.connector import Error

import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "resume_analyzer"),
}

# A basic skills dictionary the analyzer looks for. Extend as needed.
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "mysql",
    "postgresql", "mongodb", "html", "css", "react", "angular", "vue",
    "node.js", "flask", "django", "spring", "aws", "azure", "gcp", "docker",
    "kubernetes", "git", "linux", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "tensorflow", "pytorch", "nlp",
    "rest api", "graphql", "excel", "power bi", "tableau", "agile", "scrum",
    "communication", "leadership", "project management", "problem solving",
]

app = Flask(__name__, template_folder=".")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------------------------------
# DB helpers
# --------------------------------------------------------------------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def save_resume_record(filename, raw_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resumes (filename, raw_text) VALUES (%s, %s)",
        (filename, raw_text),
    )
    conn.commit()
    resume_id = cur.lastrowid
    cur.close()
    conn.close()
    return resume_id


def save_job_description(title, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO job_descriptions (title, description) VALUES (%s, %s)",
        (title, description),
    )
    conn.commit()
    job_id = cur.lastrowid
    cur.close()
    conn.close()
    return job_id


def save_analysis_result(resume_id, job_id, score, matched, missing):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO analysis_results
           (resume_id, job_id, match_score, matched_skills, missing_skills)
           VALUES (%s, %s, %s, %s, %s)""",
        (resume_id, job_id, score, ",".join(matched), ",".join(missing)),
    )
    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_stream):
    document = docx.Document(file_stream)
    return "\n".join(p.text for p in document.paragraphs)


def extract_text(file_storage):
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    stream = io.BytesIO(file_storage.read())

    if ext == "pdf":
        return extract_text_from_pdf(stream)
    elif ext == "docx":
        return extract_text_from_docx(stream)
    elif ext == "txt":
        return stream.read().decode("utf-8", errors="ignore")
    return ""


# --------------------------------------------------------------------------
# Analysis logic
# --------------------------------------------------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compute_match_score(resume_text, job_text):
    """TF-IDF + cosine similarity -> 0-100 score."""
    documents = [clean_text(resume_text), clean_text(job_text)]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)


def extract_skills(text, skill_list=SKILL_KEYWORDS):
    text_clean = clean_text(text)
    found = []
    for skill in skill_list:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_clean):
            found.append(skill)
    return found


def analyze(resume_text, job_text):
    score = compute_match_score(resume_text, job_text)
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))

    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()
    job_title = request.form.get("job_title", "Untitled Role").strip()

    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    try:
        resume_text = extract_text(resume_file)
    except Exception as e:
        return jsonify({"error": f"Could not read resume file: {e}"}), 400
    if not resume_text.strip():
        return jsonify({"error": "Could not extract text from resume"}), 400

    try:
        result = analyze(resume_text, job_description)
    except ValueError as e:
        return jsonify({"error": f"Could not analyze resume: {e}"}), 400

    # Persist to MySQL (skips gracefully if DB is unavailable)
    try:
        resume_id = save_resume_record(resume_file.filename, resume_text)
        job_id = save_job_description(job_title, job_description)
        save_analysis_result(
            resume_id, job_id, result["score"],
            result["matched_skills"], result["missing_skills"],
        )
        result["saved"] = True
    except Error as e:
        result["saved"] = False
        result["db_error"] = str(e)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
