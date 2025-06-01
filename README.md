# 🤖 Smart ATS Resume Scanner

This project is an AI-powered Smart ATS (Applicant Tracking System) built using **Google Gemini**, **Streamlit**, and **PyPDF2**, designed to evaluate resumes against job descriptions and provide intelligent feedback on keyword matches, missing skills, and profile relevance.

---

## 🔍 Features

- 📄 Upload any **PDF Resume**
- 🧠 Paste a **Job Description**
- 💡 Gemini AI evaluates match score, missing keywords, and gives a **profile summary**
- 📊 Helps you tailor your resume for competitive roles in **Data Science**, **Data Analytics**, **Software Engineering**, and **Big Data**

---

## 🖼️ Demo

<img src="ats_demo.gif" alt="Smart ATS Demo" width="100%"/>

---

## 🚀 How It Works

1. Upload your PDF resume
2. Paste the target job description
3. Gemini AI compares the resume content and JD
4. Outputs a JSON-style or formatted text summary:
   - ✅ JD Match %
   - ❌ Missing Keywords
   - 📄 Profile Summary

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/)
- [Google Generative AI (Gemini)](https://ai.google.dev/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [dotenv](https://pypi.org/project/python-dotenv/)

---

## 📁 Project Structure

smart-ats-resume-scanner/
│
├── app.py # Main Streamlit app
├── .env # Store your Google API Key
├── requirements.txt # Dependencies
└── README.md # Project Overview

yaml
Copy
Edit




## 🛠️ Setup Instructions

#### 1. Clone the Repo

bash
git clone https://github.com/your-username/smart-ats-resume-scanner.git
cd smart-ats-resume-scanner ```


#### 2. Create a Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


#### 3. Install Requirements

pip install -r requirements.txt


4. Add Google API Key
Create a .env file with:

GOOGLE_API_KEY=your_google_api_key_here
Get your key from: https://ai.google.dev

### ▶️ Run the App

streamlit run app.py


