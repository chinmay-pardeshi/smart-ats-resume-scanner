import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = st.secrets("GOOGLE_API_KEY")

# Configure Gemini
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("❌ GOOGLE_API_KEY not found. Please set it in a .env file.")
    st.stop()

# Function to call Gemini
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('models/learnlm-2.0-flash-experimental')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error from Gemini: {str(e)}"

# Function to extract PDF text
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Streamlit UI
st.title("📄 Smart ATS - Resume Evaluator")
st.markdown("Improve your resume based on job description using AI")

jd = st.text_area("📌 Paste the Job Description Here")
uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF Only)", type="pdf", help="Upload your resume in PDF format")
submit = st.button("🔍 Evaluate Resume")

if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner("Analyzing resume..."):
            resume_text = input_pdf_text(uploaded_file)

            input_prompt = f"""
Act like a highly experienced ATS (Applicant Tracking System) with expertise in evaluating tech resumes
for roles in software engineering, data science, data analytics, and big data engineering.

Your job is to evaluate the following resume against the provided job description.

Please return your analysis in a human-friendly report format with the following sections:
1. JD Match: Percentage match between resume and JD
2. Missing Keywords: A bulleted list of important keywords or skills missing in the resume
3. Profile Summary: A brief summary explaining how well the resume aligns with the JD and suggestions for improvement

Avoid JSON or code-like formats. Just return well-formatted, readable text.

Resume:
{resume_text}

Job Description:
{jd}
"""

            # Get Gemini response
            response_text = get_gemini_response(input_prompt)

            st.subheader("📊 ATS Evaluation Result")
            st.markdown(response_text)

    else:
        st.warning("⚠️ Please upload a resume and provide a job description.")


