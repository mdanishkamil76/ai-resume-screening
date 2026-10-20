# AI Resume Screening Assistant

A Streamlit application using two Groq-powered AI agents.

## Features

### Agent 1: ATS Compliance
- Resume text extraction checks
- Standard section detection
- Employment date and chronology review
- Common ATS readability recommendations
- ATS readiness estimate

### Agent 2: Job Description Matching
- Job requirement analysis
- Skills and experience matching
- Matched and missing requirements
- Evidence-based recommendations
- Suggested interview questions

## Technology Stack

- Python
- Streamlit
- Groq API
- PyMuPDF
- python-docx
- GitHub
- Streamlit Community Cloud

## Supported Resume Formats

- PDF
- DOCX
- TXT

## Local Installation

Install Python 3.10 or newer.

Install dependencies:

    pip install -r requirements.txt

Configure your Groq API key using Streamlit secrets
or the application's API key input.

Start the application:

    streamlit run app.py

## Deployment

1. Upload the project files to GitHub.
2. Open Streamlit Community Cloud.
3. Connect your GitHub repository.
4. Set the entry point to app.py.
5. Configure GROQ_API_KEY in Streamlit secrets.
6. Deploy the application.

## Security and Responsible Use

- Never commit API keys to GitHub.
- Protect candidate information.
- Review applicable privacy and data retention requirements.
- Verify AI findings against the original resume.
- Do not use AI scores as the sole basis for hiring decisions.

## Limitations

The ATS score is an advisory estimate, not an official
score from any ATS vendor. Scanned PDFs are not OCR-processed.
