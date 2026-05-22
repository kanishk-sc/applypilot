import streamlit as st
from utils import calculate_match_score, find_missing_skills

st.set_page_config(page_title="ApplyPilot", layout="wide")

st.title("ApplyPilot")
st.subheader("AI Job Application Workflow Assistant")

st.write("Paste a job description below to compare it with your resume.")

with open("resume.txt", "r", encoding="utf-8") as file:
    resume_text = file.read()

job_text = st.text_area("Paste Job Description", height=300)

if st.button("Analyze Job"):
    if not job_text.strip():
        st.warning("Please paste a job description first.")
    else:
        score = calculate_match_score(resume_text, job_text)
        resume_skills, job_skills, missing = find_missing_skills(resume_text, job_text)

        st.metric("Resume Match Score", f"{score}%")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Your Resume Skills")
            st.write(resume_skills)

        with col2:
            st.subheader("Job Required Skills")
            st.write(job_skills)

        with col3:
            st.subheader("Missing Skills")
            st.write(missing)

        st.subheader("Cover Letter Draft")

        company_placeholder = "[Company Name]"
        role_placeholder = "[Role Title]"

        cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for the {role_placeholder} position at {company_placeholder}. 
My background in Information Technology, software development, data analysis, and database systems aligns well with this role.

Based on the job description, I noticed emphasis on {", ".join(job_skills[:5])}. 
Through my academic projects and hands-on experience, I have worked with technologies such as {", ".join(resume_skills[:6])}.

I would welcome the opportunity to contribute my technical skills, problem-solving ability, and eagerness to learn to your team.

Sincerely,  
Kanishk Singh Chauhan
"""

        st.text_area("Generated Draft", cover_letter, height=250)