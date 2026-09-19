import os

import httpx
import streamlit as st

API_URL = os.getenv("APPLYPILOT_API_URL", "http://localhost:8010")


def api_request(method: str, path: str, **kwargs):
    try:
        response = httpx.request(method, f"{API_URL}{path}", timeout=45, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.json().get("detail", "request_failed")
        st.error(f"ApplyPilot API error: {detail}")
    except httpx.HTTPError:
        st.error("ApplyPilot API is unavailable. Start the Docker Compose stack first.")
    return None


st.set_page_config(page_title="ApplyPilot", layout="wide")
st.title("ApplyPilot")
st.caption("Explainable resume-to-role matching; not a commercial ATS score.")

analyze_tab, history_tab = st.tabs(["Analyze", "Analysis history"])

with analyze_tab:
    uploaded_resume = st.file_uploader("Resume", type=["pdf", "txt"])
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Role title")
    with col2:
        company = st.text_input("Company (optional)")
    job_description = st.text_area("Job description", height=280)

    if st.button("Calculate match", type="primary"):
        if (
            not uploaded_resume
            or not title.strip()
            or len(job_description.strip()) < 50
        ):
            st.warning(
                "Upload a resume and provide a role plus a substantive job description."
            )
        else:
            resume = api_request(
                "POST",
                "/api/resumes",
                files={
                    "file": (
                        uploaded_resume.name,
                        uploaded_resume.getvalue(),
                        uploaded_resume.type,
                    )
                },
            )
            job = api_request(
                "POST",
                "/api/jobs",
                json={
                    "title": title,
                    "company": company or None,
                    "description": job_description,
                },
            )
            if resume and job:
                analysis = api_request(
                    "POST",
                    "/api/analyses",
                    json={
                        "resume_id": resume["resume_id"],
                        "job_id": job["job_id"],
                    },
                )
                if analysis:
                    st.session_state.analysis = analysis

    analysis = st.session_state.get("analysis")
    if analysis:
        st.metric("Resume-to-Role Match", f"{analysis['match_score']:.1f}%")
        columns = st.columns(4)
        labels = {
            "semantic_similarity": "Semantic",
            "skills_coverage": "Skills",
            "keyword_coverage": "Keywords",
            "experience_alignment": "Experience",
        }
        for column, (key, label) in zip(columns, labels.items(), strict=True):
            column.metric(label, f"{analysis['components'][key]:.1f}%")
        st.subheader("Evidence")
        st.write("Matched skills:", analysis["matched_skills"] or "None detected")
        st.write("Missing skills:", analysis["missing_skills"] or "None detected")
        st.write("Matched keywords:", analysis["matched_keywords"] or "None detected")

        st.subheader("Grounded generation")
        generation_kind = st.selectbox(
            "Output",
            ["cover_letter", "recruiter_message", "gap_explanation"],
            format_func=lambda value: value.replace("_", " ").title(),
        )
        if st.button("Generate with OpenAI"):
            generated = api_request(
                "POST",
                f"/api/analyses/{analysis['analysis_id']}/generate",
                json={"kind": generation_kind},
            )
            if generated:
                st.session_state.generated = generated["content"]
        if st.session_state.get("generated"):
            st.text_area("Generated draft", st.session_state.generated, height=300)

with history_tab:
    if st.button("Refresh history"):
        st.session_state.history = api_request("GET", "/api/analyses") or []
    history = st.session_state.get("history", [])
    if not history:
        st.info("No persisted analyses loaded yet.")
    for item in history:
        with st.expander(
            f"{item['match_score']:.1f}% — analysis {item['analysis_id']}"
        ):
            st.json(item)
