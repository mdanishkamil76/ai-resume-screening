import json
import streamlit as st
from groq import Groq

from resume_parser import extract_resume_text, get_file_signals
from agents import (
    run_ats_agent,
    run_matching_agent,
    run_resume_redesign_agent
)

from resume_builder import build_resume_docx

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide"
)

st.title("AI Resume Screening Assistant")
st.write("Two AI agents for ATS compliance and job-description matching.")

st.warning(
    "This application provides decision support, not hiring decisions. "
    "Verify results against the original resume and job requirements."
)

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Groq API key", type="password")
    model = st.text_input("Groq model", value="openai/gpt-oss-20b")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

resume_file = st.file_uploader(
    "Upload candidate resume",
    type=["pdf", "docx", "txt"]
)

job_description = st.text_area(
    "Paste the complete job description",
    height=250
)

if st.button(
    "Analyze Resume",
    type="primary",
    disabled=not (
        resume_file and job_description.strip() and api_key
    )
):
    try:
        client = Groq(api_key=api_key)

        with st.spinner("Extracting resume text..."):
            resume_text = extract_resume_text(resume_file)
            file_signals = get_file_signals(
                resume_file, resume_text
            )

        if len(resume_text.strip()) < 80:
            st.error(
                "Insufficient text extracted. This may be a "
                "scanned PDF. Try a searchable PDF or DOCX."
            )
            st.stop()

        with st.spinner("Agent 1: Checking ATS compliance..."):
            ats = run_ats_agent(
                client, model, resume_text, file_signals
            )

        with st.spinner("Agent 2: Matching job requirements..."):
            match = run_matching_agent(
                client, model, resume_text, job_description
            )
with st.spinner("Agent 3: Redesigning the resume..."):
    redesigned_resume = run_resume_redesign_agent(
        client=client,
        model=model,
        resume_text=resume_text,
        job_description=job_description,
        ats_result=ats,
        match_result=match
    )

resume_docx = build_resume_docx(redesigned_resume)

st.session_state["redesigned_resume"] = redesigned_resume
st.session_state["resume_docx"] = resume_docx
        summary = (
            f"ATS readiness estimate: {ats['score']}/100\n"
            f"{ats['overall_assessment']}\n\n"
            f"Job match estimate: {match['match_score']}/100\n"
            f"{match['overall_assessment']}\n\n"
            "Human verification is required before making "
            "any hiring decision."
        )

        report = {
            "resume_file": resume_file.name,
            "ats_agent": ats,
            "matching_agent": match,
            "hr_summary": summary,
            "file_signals": file_signals
        }

        st.session_state["report"] = report

    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.info(
            "Check your API key, model availability, "
            "internet connection, and Groq API quota."
        )

report = st.session_state.get("report")

if report:
    ats = report["ats_agent"]
    match = report["matching_agent"]

    st.divider()
    st.header("Screening Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "ATS Readiness Estimate",
            f"{ats['score']}/100"
        )

    with col2:
        st.metric(
            "Job Description Match",
            f"{match['match_score']}/100"
        )

    st.subheader("HR Summary")
    st.write(report["hr_summary"])

    tab1, tab2, tab3, tab4 = st.tabs([
        "ATS Agent",
        "Matching Agent",
        "Requirements",
        "Export"
    ])

    with tab1:
        st.write(ats["overall_assessment"])

        st.markdown("**Strengths**")
        for item in ats["strengths"]:
            st.write(f"- {item}")

        st.markdown("**Issues identified**")
        for item in ats["issues"]:
            st.write(f"- {item}")

        st.markdown("**Recommendations**")
        for item in ats["recommendations"]:
            st.write(f"- {item}")

        st.markdown("**File extraction signals**")
        st.json(report["file_signals"])

    with tab2:
        st.write(match["overall_assessment"])

        st.markdown("**Relevant strengths**")
        for item in match["strengths"]:
            st.write(f"- {item}")

        st.markdown("**Gaps or missing evidence**")
        for item in match["gaps"]:
            st.write(f"- {item}")

        st.markdown("**Resume improvement recommendations**")
        for item in match["recommendations"]:
            st.write(f"- {item}")

        st.markdown("**Suggested interview questions**")
        for item in match["interview_questions"]:
            st.write(f"- {item}")

    with tab3:
        st.markdown("**Matched requirements**")
        st.dataframe(
            match["matched_requirements"],
            use_container_width=True
        )

        st.markdown("**Missing or unclear requirements**")
        st.dataframe(
            match["missing_requirements"],
            use_container_width=True
        )

        st.caption(
            "Not evidenced in a resume does not necessarily "
            "mean the candidate lacks the qualification."
        )

    with tab4:
        json_data = json.dumps(
            report, indent=2, ensure_ascii=False
        )

        st.download_button(
            "Download JSON report",
            data=json_data,
            file_name="resume_screening_report.json",
            mime="application/json"
        )

        st.download_button(
            "Download HR summary",
            data=report["hr_summary"],
            file_name="hr_summary.txt",
            mime="text/plain"
        )
st.subheader("Agent 3: Redesigned Resume")

redesigned = st.session_state.get("redesigned_resume")

if redesigned:
    st.write(
        redesigned.get("professional_summary", "")
    )

    st.markdown("### Core Skills")

    st.write(
        " | ".join(redesigned.get("core_skills", []))
    )

    st.markdown("### Professional Experience")

    for job in redesigned.get("experience", []):
        st.markdown(
            f"**{job.get('job_title', '')} — "
            f"{job.get('employer', '')}**"
        )

        if job.get("dates"):
            st.caption(job["dates"])

        for bullet in job.get("bullets", []):
            st.write(f"- {bullet}")

    if redesigned.get("items_to_confirm"):
        st.warning(
            "Please verify these details before using the resume."
        )

        for item in redesigned["items_to_confirm"]:
            st.write(f"- {item}")

    st.download_button(
        label="Download Redesigned Resume (Word)",
        data=st.session_state["resume_docx"],
        file_name="redesigned_resume.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )
