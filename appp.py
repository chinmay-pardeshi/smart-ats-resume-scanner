# import streamlit as st
# import google.generativeai as genai
# import os
# import PyPDF2 as pdf
# from dotenv import load_dotenv
# import json

# load_dotenv() ## load all our environment variables

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_gemini_repsonse(input):
#     model=genai.GenerativeModel('models/learnlm-2.0-flash-experimental')
#     response=model.generate_content(input)
#     return response.text

# def input_pdf_text(uploaded_file):
#     reader=pdf.PdfReader(uploaded_file)
#     text=""
#     for page in range(len(reader.pages)):
#         page=reader.pages[page]
#         text+=str(page.extract_text())
#     return text

# #Prompt Template

# input_prompt="""
# Hey Act Like a skilled or very experience ATS(Application Tracking System)
# with a deep understanding of tech field,software engineering,data science ,data analyst
# and big data engineer. Your task is to evaluate the resume based on the given job description.
# You must consider the job market is very competitive and you should provide 
# best assistance for improving thr resumes. Assign the percentage Matching based 
# on Jd and
# the missing keywords with high accuracy
# resume:{text}
# description:{jd}

# I want the response in one single string having the structure
# {{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
# """

# ## streamlit app
# st.title("Smart ATS")
# st.text("Improve Your Resume ATS")
# jd=st.text_area("Paste the Job Description")
# uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

# submit = st.button("Submit")

# if submit:
#     if uploaded_file is not None:
#         text=input_pdf_text(uploaded_file)
#         response=get_gemini_repsonse(input_prompt)
#         st.subheader(response)





import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import ast  # For safely parsing stringified dicts

# Load environment variables from .env (e.g., GOOGLE_API_KEY)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(prompt):
    model = genai.GenerativeModel('models/learnlm-2.0-flash-experimental')
    response = model.generate_content(prompt)
    return response.text

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Streamlit UI
st.title("📄 Smart ATS - Resume Evaluator")
st.markdown("Improve your resume based on job description using AI")

# Input fields
jd = st.text_area("📌 Paste the Job Description Here")
uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF Only)", type="pdf", help="Upload your resume in PDF format")

submit = st.button("🔍 Evaluate Resume")

# Run when button is clicked
if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner("Analyzing resume..."):
            resume_text = input_pdf_text(uploaded_file)

            # Proper prompt with actual data inserted
           # Updated natural language prompt
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
            # Just display it directly, no need to parse JSON
            response_text = get_gemini_response(input_prompt)

            st.subheader("📊 ATS Evaluation Result")
            st.markdown(response_text)

       

        try:
            # Parse the stringified dictionary response from Gemini
            parsed = ast.literal_eval(response_text.strip())

            # Display JD Match %
            st.markdown(f"### ✅ JD Match: `{parsed.get('JD Match', 'N/A')}`")

            # Display Missing Keywords
            missing_keywords = parsed.get("MissingKeywords", [])
            if missing_keywords:
                st.markdown("### ❌ Missing Keywords:")
                for keyword in missing_keywords:
                    st.markdown(f"- {keyword}")
            else:
                st.markdown("✅ No missing keywords found!")

            # Display Profile Summary
            profile_summary = parsed.get("Profile Summary", "")
            if profile_summary:
                st.markdown("### 📝 Profile Summary:")
                st.markdown(profile_summary)

        except Exception as e:
            st.error("⚠️ Could not parse the AI response as JSON.")
            st.markdown("### Raw Response:")
            st.code(response_text)

    else:
        st.warning("⚠️ Please upload a resume and provide a job description.")
