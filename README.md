# ApplyPilot

AI-powered job application assistant that helps automate parts of the job search process.

## Features

- Resume match scoring against job descriptions
- AI-generated cover letters
- Recruiter outreach message generation
- Resume upload and PDF parsing
- Job-specific keyword extraction
- ATS optimization suggestions

## Tech Stack

- Python
- Streamlit
- GitHub Actions
- PyPDF
- OpenAI API

## Architecture

1. User uploads resume
2. User pastes job description
3. Resume is parsed and analyzed
4. AI generates tailored outputs
5. Results are displayed through a Streamlit interface

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py