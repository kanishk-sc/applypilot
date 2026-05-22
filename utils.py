import re
from io import BytesIO
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

COMMON_SKILLS = [
    "python", "sql", "javascript", "java", "react", "node.js", "fastapi",
    "flask", "django", "postgresql", "mysql", "mongodb", "sqlite",
    "power bi", "tableau", "excel", "git", "github", "linux",
    "docker", "aws", "azure", "rest api", "api", "html", "css",
    "data analysis", "data visualization", "etl", "pandas", "numpy",
    "machine learning", "authentication", "database", "agile"
]

def clean_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_text_from_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    if file_name.endswith(".pdf"):
        pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    return ""

def extract_name(resume_text):
    lines = resume_text.strip().split("\n")

    for line in lines:
        cleaned = line.strip()

        if len(cleaned.split()) >= 2 and len(cleaned) < 60:
            return cleaned

    return "Applicant"

def extract_skills(text):
    text = clean_text(text)
    found = []

    for skill in COMMON_SKILLS:
        if skill in text:
            found.append(skill)

    return sorted(set(found))

def calculate_match_score(resume_text, job_text):
    documents = [resume_text, job_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

def find_missing_skills(resume_text, job_text):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    missing = [skill for skill in job_skills if skill not in resume_skills]

    return resume_skills, job_skills, missing