import streamlit as st
from utils import calculate_match_score, find_missing_skills, extract_name

st.set_page_config(page_title="ApplyPilot", layout="wide")

st.title("ApplyPilot")
st.subheader("AI Job Application Workflow Assistant")

st.write("Upload your resume, paste a job description, and get a match score, missing skills, and a cover letter draft.")

uploaded_resume = st.file_uploader("Upload Resume (.txt only for now)", type=["txt"])

job_text = st.text_area("Paste Job Description", height=300)

if st.button("Analyze Job"):
    if uploaded_resume is None:
        st.warning("Please upload your resume as a .txt file.")
    elif not job_text.strip():
        st.warning("Please paste a job description first.")
    else:
        resume_text = uploaded_resume.read().decode("utf-8")
        candidate_name = extract_name(resume_text)

        score = calculate_match_score(resume_text, job_text)
        resume_skills, job_skills, missing = find_missing_skills(resume_text, job_text)

        st.metric("Resume Match Score", f"{score}%")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Resume Skills Found")
            st.write(resume_skills)

        with col2:
            st.subheader("Job Skills Found")
            st.write(job_skills)

        with col3:
            st.subheader("Missing Skills")
            st.write(missing)

        st.subheader("Cover Letter Draft")

        cover_letter = f"""
Dear Hiring Manager,

I am excited to apply for this position. My background in Information Technology, software development, data analysis, and database systems aligns well with the role.

Based on the job description, I noticed emphasis on {", ".join(job_skills[:5])}. Through my academic projects and hands-on experience, I have worked with technologies such as {", ".join(resume_skills[:6])}.

I would welcome the opportunity to contribute my technical skills, problem-solving ability, and eagerness to learn to your team.

Sincerely,  
{candidate_name}
"""

        st.text_area("Generated Draft", cover_letter, height=250)