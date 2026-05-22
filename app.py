import streamlit as st
import pandas as pd

from utils import (
    extract_text_from_file,
    extract_name,
    find_missing_skills,
    calculate_match_score,
    get_fit_rating,
    generate_resume_bullets,
    generate_cover_letter,
    generate_recruiter_message,
    generate_interview_questions,
    init_db,
    save_application,
    load_applications,
    top_missing_skills,
    extract_skills,
    SOFT_SKILLS
)

st.set_page_config(page_title="ApplyPilot", layout="wide")
init_db()

if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""

if "recruiter_message" not in st.session_state:
    st.session_state.recruiter_message = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = {}

st.sidebar.title("ApplyPilot")
page = st.sidebar.radio(
    "Navigate",
    ["Analyze Job", "Compare Resumes", "Application Tracker", "Dashboard"]
)

if page == "Analyze Job":
    st.title("ApplyPilot")
    st.subheader("AI Job Application Workflow Assistant")

    uploaded_resume = st.file_uploader("Upload Resume (.pdf or .txt)", type=["pdf", "txt"])
    job_text = st.text_area("Paste Job Description", height=280)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        company = st.text_input("Company Name")
    with col_b:
        role = st.text_input("Role Title")
    with col_c:
        tone = st.selectbox("Cover Letter Tone", ["Professional", "Concise"])

    status = st.selectbox("Application Status", ["Interested", "Applied", "Interviewing", "Rejected", "Offer"])
    notes = st.text_area("Notes", height=80)

    if st.button("Analyze Job"):
        if uploaded_resume is None:
            st.warning("Please upload your resume.")
        elif not job_text.strip():
            st.warning("Please paste a job description.")
        else:
            resume_text = extract_text_from_file(uploaded_resume)

            if not resume_text.strip():
                st.error("Could not extract text from the resume.")
                st.stop()

            candidate_name = extract_name(resume_text)

            score = calculate_match_score(resume_text, job_text)
            resume_skills, job_skills, missing = find_missing_skills(resume_text, job_text)
            soft_skills_found = extract_skills(job_text, SOFT_SKILLS)
            fit_rating = get_fit_rating(score, len(missing))

            st.session_state.cover_letter = generate_cover_letter(
                candidate_name, company, role, resume_skills, job_skills, tone
            )

            st.session_state.recruiter_message = generate_recruiter_message(
                candidate_name, company, role
            )

            st.session_state.questions = generate_interview_questions(job_skills)

            st.session_state.analysis_data = {
                "company": company,
                "role": role,
                "score": score,
                "resume_skills": resume_skills,
                "job_skills": job_skills,
                "missing": missing,
                "soft_skills_found": soft_skills_found,
                "fit_rating": fit_rating,
                "status": status,
                "notes": notes,
            }

            st.session_state.analysis_done = True

    if st.session_state.analysis_done:
        data = st.session_state.analysis_data

        st.metric("Resume Match Score", f"{data['score']}%")
        st.success(f"Job Fit Rating: {data['fit_rating']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("Resume Skills Found")
            st.write(data["resume_skills"])

        with col2:
            st.subheader("Job Skills Found")
            st.write(data["job_skills"])

        with col3:
            st.subheader("Missing Skills")
            st.write(data["missing"])

        with col4:
            st.subheader("Soft Skills Found")
            st.write(data["soft_skills_found"])

        st.subheader("Resume Bullet Suggestions")
        for bullet in generate_resume_bullets(data["missing"]):
            st.write(f"- {bullet}")

        st.subheader("Cover Letter Draft")
        st.text_area(
            "Generated Cover Letter",
            st.session_state.cover_letter,
            height=260
        )

        st.download_button(
            "Download Cover Letter",
            st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain"
        )

        st.subheader("Recruiter Message")
        st.code(st.session_state.recruiter_message, language=None)
        st.caption("Click the copy icon in the top-right corner to copy.")

        st.subheader("Interview Prep Questions")
        for q in st.session_state.questions:
            st.write(f"- {q}")

        if st.button("Save Application"):
            save_application(
                data["company"],
                data["role"],
                data["score"],
                data["fit_rating"],
                data["missing"],
                data["status"],
                data["notes"]
            )
            st.success("Application saved.")

elif page == "Compare Resumes":
    st.title("Resume Version Comparison")

    resume_a = st.file_uploader("Upload Resume A", type=["pdf", "txt"], key="resume_a")
    resume_b = st.file_uploader("Upload Resume B", type=["pdf", "txt"], key="resume_b")
    job_text = st.text_area("Paste Job Description", height=280)

    if st.button("Compare"):
        if resume_a is None or resume_b is None or not job_text.strip():
            st.warning("Upload both resumes and paste a job description.")
        else:
            text_a = extract_text_from_file(resume_a)
            text_b = extract_text_from_file(resume_b)

            score_a = calculate_match_score(text_a, job_text)
            score_b = calculate_match_score(text_b, job_text)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Resume A Score", f"{score_a}%")
            with col2:
                st.metric("Resume B Score", f"{score_b}%")

            if score_a > score_b:
                st.success("Resume A is a better match for this job.")
            elif score_b > score_a:
                st.success("Resume B is a better match for this job.")
            else:
                st.info("Both resumes have the same match score.")

elif page == "Application Tracker":
    st.title("Application Tracker")

    df = load_applications()

    if df.empty:
        st.info("No applications saved yet.")
    else:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "Download Applications CSV",
            csv,
            file_name="applications.csv",
            mime="text/csv"
        )

elif page == "Dashboard":
    st.title("Application Dashboard")

    df = load_applications()

    if df.empty:
        st.info("No application data available yet.")
    else:
        total_apps = len(df)
        avg_score = round(df["match_score"].mean(), 2)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Applications", total_apps)
        with col2:
            st.metric("Average Match Score", f"{avg_score}%")

        st.subheader("Applications by Status")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.subheader("Match Scores")
        chart_df = df[["company", "role", "match_score"]].copy()
        chart_df["label"] = chart_df["company"].fillna("") + " - " + chart_df["role"].fillna("")
        st.bar_chart(chart_df.set_index("label")["match_score"])

        st.subheader("Top Missing Skills")
        missing = top_missing_skills(df)

        if missing:
            missing_df = pd.DataFrame(missing, columns=["Skill", "Count"])
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.info("No missing skills recorded.")