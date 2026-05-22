import re
import sqlite3
from io import BytesIO
from datetime import datetime
from collections import Counter

import pandas as pd
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

COMMON_SKILLS = [
    "python", "sql", "javascript", "java", "react", "node.js", "fastapi", "flask",
    "django", "postgresql", "mysql", "mongodb", "sqlite", "power bi", "tableau",
    "excel", "git", "github", "linux", "docker", "aws", "azure", "rest api", "api",
    "html", "css", "data analysis", "data visualization", "etl", "pandas", "numpy",
    "machine learning", "authentication", "database", "agile", "jira", "scrum",
    "typescript", "c++", "c#", "cloud", "ci/cd", "testing", "unit testing",
    "debugging", "troubleshooting", "customer support", "help desk", "security",
    "splunk", "power automate", "sharepoint"
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving", "collaboration",
    "attention to detail", "organization", "adaptability", "time management",
    "analytical", "critical thinking"
]

DB_NAME = "applications.db"


def clean_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_text_from_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if file_name.endswith(".pdf"):
        reader = PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    return ""


def extract_name(resume_text):
    lines = resume_text.strip().split("\n")
    for line in lines[:8]:
        cleaned = line.strip()
        if 2 <= len(cleaned.split()) <= 5 and len(cleaned) < 60:
            return cleaned
    return "Applicant"


def extract_skills(text, skill_list=COMMON_SKILLS):
    text = clean_text(text)
    return sorted({skill for skill in skill_list if skill in text})


def calculate_match_score(resume_text, job_text):
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_text)

    resume_skills = extract_skills(resume_text, COMMON_SKILLS)
    job_skills = extract_skills(job_text, COMMON_SKILLS)

    resume_soft = extract_skills(resume_text, SOFT_SKILLS)
    job_soft = extract_skills(job_text, SOFT_SKILLS)

    if job_skills:
        skill_score = len(set(resume_skills) & set(job_skills)) / len(set(job_skills))
    else:
        skill_score = 0

    if job_soft:
        soft_score = len(set(resume_soft) & set(job_soft)) / len(set(job_soft))
    else:
        soft_score = 0.5

    important_terms = [
        "develop", "design", "analyze", "support", "troubleshoot",
        "dashboard", "database", "reporting", "automation", "testing",
        "deployment", "documentation", "collaborate", "optimize",
        "monitor", "maintain", "integrate", "debug"
    ]

    matched_terms = [
        term for term in important_terms
        if term in resume_clean and term in job_clean
    ]

    responsibility_score = len(matched_terms) / len(important_terms)

    final_score = (
        skill_score * 0.60 +
        responsibility_score * 0.25 +
        soft_score * 0.15
    )

    return round(final_score * 100, 2)


def find_missing_skills(resume_text, job_text):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    missing = [skill for skill in job_skills if skill not in resume_skills]
    return resume_skills, job_skills, missing


def get_fit_rating(score, missing_count):
    if score >= 70 and missing_count <= 4:
        return "Strong Fit"
    if score >= 45:
        return "Moderate Fit"
    return "Weak Fit"


def generate_resume_bullets(missing_skills):
    if not missing_skills:
        return ["Your resume already covers the main detected skills from this job."]

    bullets = []
    for skill in missing_skills[:5]:
        bullets.append(f"Add a resume bullet or project detail showing hands-on experience with {skill}.")
    return bullets


def generate_cover_letter(candidate_name, company, role, resume_skills, job_skills, tone):
    company = company or "your company"
    role = role or "this position"

    if tone == "Concise":
        return f"""Dear Hiring Manager,

I am excited to apply for the {role} position at {company}. My background includes experience with {", ".join(resume_skills[:6])}, and the role's focus on {", ".join(job_skills[:5])} closely matches my technical interests.

I would welcome the opportunity to contribute my problem-solving ability, technical skills, and willingness to learn to your team.

Sincerely,
{candidate_name}
"""

    return f"""Dear Hiring Manager,

I am excited to apply for the {role} position at {company}. My background in information technology, software development, data analysis, and database systems aligns well with this opportunity.

Based on the job description, I noticed emphasis on {", ".join(job_skills[:5])}. Through my academic projects and hands-on experience, I have worked with technologies such as {", ".join(resume_skills[:6])}, and I am confident in my ability to quickly learn and contribute in this role.

I would welcome the opportunity to bring my technical skills, problem-solving mindset, and strong work ethic to your team.

Sincerely,
{candidate_name}
"""


def generate_recruiter_message(candidate_name, company, role):
    return f"""Hi,

I recently came across the {role or "open"} position at {company or "your company"} and wanted to reach out. My background includes IT, software development, data analysis, and database-related project work, and I am very interested in contributing to your team.

I would appreciate the opportunity to connect and learn more about the role.

Best,
{candidate_name}
"""


def generate_interview_questions(job_skills):
    questions = [
        "Tell me about yourself and why you are interested in this role.",
        "Describe a project where you solved a technical problem.",
        "Tell me about a time you had to learn a new tool quickly."
    ]

    for skill in job_skills[:5]:
        questions.append(f"How have you used {skill} in a project or work environment?")

    return questions


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            match_score REAL,
            fit_rating TEXT,
            missing_skills TEXT,
            status TEXT,
            notes TEXT,
            date_added TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_application(company, role, score, fit_rating, missing_skills, status, notes):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO applications 
        (company, role, match_score, fit_rating, missing_skills, status, notes, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company, role, score, fit_rating, ", ".join(missing_skills),
        status, notes, datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()


def load_applications():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM applications ORDER BY id DESC", conn)
    conn.close()
    return df


def top_missing_skills(df):
    all_skills = []
    for item in df["missing_skills"].dropna():
        all_skills.extend([skill.strip() for skill in item.split(",") if skill.strip()])
    return Counter(all_skills).most_common(10)