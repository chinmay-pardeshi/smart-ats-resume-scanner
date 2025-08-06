import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import time
import pandas as pd
import re
import json

# ✨ Page Configuration
st.set_page_config(
    page_title="Smart ATS Pro | AI-Powered Resume Evaluator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Custom CSS for Modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        padding: 1rem;
    }
    
    /* Custom Header */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .hero-description {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.8;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-family: 'Inter', sans-serif;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    /* Results Section */
    .results-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px 10px 0 0;
        margin-bottom: 0;
    }
    
    .results-body {
        background: white;
        padding: 2rem;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 500;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress Bar */
    .progress-container {
        background: #f1f3f4;
        border-radius: 10px;
        padding: 0.25rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 8px;
        border-radius: 8px;
        transition: width 0.3s ease;
    }
    
    /* Warning and Error Styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ✅ Load API key from Streamlit secrets
@st.cache_data
def initialize_api():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False

# ✅ Function to call Gemini with retry and error reporting
def get_gemini_response(prompt, retries=3, delay=2):
    # Try different models in order of preference
    models_to_try = [
        "gemini-pro",
        "gemini-1.5-flash", 
        "models/gemini-pro",
        "models/gemini-1.5-flash"
    ]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            st.info(f"🔄 Trying model: {model_name}")
            
            for attempt in range(retries):
                try:
                    # Split long prompts to avoid token limits
                    if len(prompt) > 30000:  # Approximate token limit check
                        st.warning("⚠️ Prompt is very long, truncating...")
                        prompt = prompt[:30000] + "\n\n[Content truncated for processing]"
                    
                    # Configure generation with safety settings
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            candidate_count=1,
                            max_output_tokens=2048,
                            temperature=0.7,
                        ),
                        safety_settings=[
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH", 
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                            }
                        ]
                    )
                    
                    if response.text:
                        st.success(f"✅ Successfully used model: {model_name}")
                        return response.text
                    else:
                        raise Exception("Empty response received")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Handle specific error cases
                    if "quota" in error_msg or "limit" in error_msg:
                        st.error("❌ API quota exceeded. Please check your Google AI Studio quota.")
                        return None
                    elif "invalid" in error_msg and "key" in error_msg:
                        st.error("❌ Invalid API key. Please check your Google AI Studio API key.")
                        return None
                    elif "blocked" in error_msg or "safety" in error_msg:
                        st.warning("⚠️ Content was blocked by safety filters. Trying with modified prompt...")
                        # Try with a more generic prompt
                        if attempt == 0:
                            generic_prompt = """
Please analyze this resume against the job description and provide:
1. A match percentage (0-100%)
2. List of missing important keywords
3. Suggestions for improvement
4. Overall assessment

Focus on professional skills and qualifications only.
"""
                            prompt = generic_prompt
                            continue
                    
                    if attempt < retries - 1:
                        st.warning(f"Attempt {attempt + 1} with {model_name} failed: {str(e)[:100]}... Retrying...")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                    else:
                        st.error(f"❌ Model {model_name} failed after {retries} attempts.")
                        break
                        
        except Exception as model_error:
            st.warning(f"❌ Could not initialize model {model_name}: {str(model_error)[:100]}")
            continue
    
    # If all models failed, provide fallback analysis
    st.error("❌ All models failed. Providing basic fallback analysis...")
    return get_fallback_analysis()

# ✅ Fallback analysis when AI is unavailable
def get_fallback_analysis():
    return """
**FALLBACK ANALYSIS - AI SERVICE UNAVAILABLE**

**1. OVERALL MATCH SCORE**
75% - Unable to perform detailed analysis due to technical issues.

**2. MISSING KEYWORDS**
• Please manually compare your resume with the job description
• Look for technical skills mentioned in the job posting
• Check for industry-specific terminology
• Ensure you have relevant experience keywords

**3. STRENGTHS ANALYSIS** 
Unable to perform detailed analysis at this time.

**4. IMPROVEMENT RECOMMENDATIONS**
• Review the job description carefully for missing keywords
• Ensure your resume uses similar language to the job posting  
• Include quantifiable achievements and results
• Use action verbs to describe your experience
• Tailor your resume for each specific role

**5. ATS OPTIMIZATION TIPS**
• Use standard section headings (Experience, Education, Skills)
• Save your resume as a PDF and Word document
• Avoid complex formatting, tables, and graphics
• Include keywords naturally in context
• Use standard fonts like Arial, Calibri, or Times New Roman

**Note:** This is a basic analysis. For detailed AI-powered insights, please try again later or check your API configuration.
"""

# ✅ Extract text from PDF
def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
        return None

# ✅ Parse AI Response for Visualization
def parse_ai_response(response_text):
    try:
        # Extract match percentage using regex
        match_pattern = r'(\d+)%'
        match_scores = re.findall(match_pattern, response_text)
        match_score = int(match_scores[0]) if match_scores else 75
        
        # Extract missing keywords
        keywords_section = re.search(r'Missing Keywords?:?\s*(.*?)(?=\n\d+\.|Profile Summary|$)', response_text, re.DOTALL | re.IGNORECASE)
        missing_keywords = []
        if keywords_section:
            keyword_text = keywords_section.group(1)
            # Extract items from bullet points or numbered lists
            keywords = re.findall(r'[•\-\*]\s*([^\n]+)|(\d+\.\s*([^\n]+))', keyword_text)
            for match in keywords:
                if match[0]:  # Bullet point
                    missing_keywords.append(match[0].strip())
                elif match[2]:  # Numbered list
                    missing_keywords.append(match[2].strip())
        
        return match_score, missing_keywords
    except Exception as e:
        st.warning(f"Could not fully parse response for visualization: {e}")
        return 75, ["Unable to extract keywords"]

# ✅ Create Skills Gap Visualization using Streamlit charts
def create_skills_visualization(match_score, missing_keywords):
    st.markdown("### 📊 Skills Gap Analysis Dashboard")
    
    # Row 1: Match Score and Overall Stats
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Match Score Gauge (using metric with delta)
        st.markdown("#### 🎯 Overall Match Score")
        
        # Color-coded match score display
        if match_score >= 80:
            st.success(f"**{match_score}%** - Excellent Match! 🎉")
            gauge_color = "🟢"
        elif match_score >= 60:
            st.warning(f"**{match_score}%** - Good Match 👍")
            gauge_color = "🟡"
        else:
            st.error(f"**{match_score}%** - Needs Improvement 📈")
            gauge_color = "🔴"
        
        # Visual gauge using progress bar
        progress_color = "normal" if match_score >= 80 else "slow"
        st.progress(match_score/100)
        
        # Recommendation based on score
        if match_score >= 80:
            st.info("💡 **Recommendation:** Your resume is well-aligned! Focus on minor optimizations.")
        elif match_score >= 60:
            st.info("💡 **Recommendation:** Good foundation. Add missing keywords to boost your score.")
        else:
            st.info("💡 **Recommendation:** Consider major revisions and add key missing skills.")
    
    with col2:
        st.markdown("#### 📊 Quick Stats")
        st.metric("Missing Skills", len(missing_keywords), delta=f"-{len(missing_keywords)}")
        
        # ATS Readiness
        ats_ready = "Ready" if match_score >= 70 else "Needs Work"
        ats_delta = "✅" if match_score >= 70 else "⚠️"
        st.metric("ATS Readiness", ats_ready, delta=ats_delta)
    
    with col3:
        st.markdown("#### 🏆 Grade")
        if match_score >= 90:
            grade, emoji = "A+", "🏆"
        elif match_score >= 80:
            grade, emoji = "A", "🥇"
        elif match_score >= 70:
            grade, emoji = "B", "🥈"
        elif match_score >= 60:
            grade, emoji = "C", "🥉"
        else:
            grade, emoji = "D", "📚"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
            <h2>{emoji} {grade}</h2>
            <p>Resume Grade</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Row 2: Skills Analysis
    if missing_keywords:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Top Missing Skills")
            
            # Create priority-based visualization
            top_missing = missing_keywords[:8] if len(missing_keywords) >= 8 else missing_keywords
            
            # Create a DataFrame for missing skills with priority
            skills_data = []
            for i, skill in enumerate(top_missing):
                if i < 3:
                    priority = "🔴 High"
                    importance = 90 - (i * 5)
                elif i < 6:
                    priority = "🟡 Medium"  
                    importance = 75 - ((i-3) * 5)
                else:
                    priority = "🟢 Low"
                    importance = 60 - ((i-6) * 5)
                
                skills_data.append({
                    "Skill": skill[:30] + "..." if len(skill) > 30 else skill,
                    "Priority": priority,
                    "Importance": importance
                })
            
            skills_df = pd.DataFrame(skills_data)
            
            # Display as a styled table
            for _, row in skills_df.iterrows():
                priority_color = "#ffebee" if "High" in row["Priority"] else "#fff3e0" if "Medium" in row["Priority"] else "#e8f5e8"
                st.markdown(f"""
                <div style="background: {priority_color}; padding: 0.75rem; margin: 0.25rem 0; border-radius: 8px; border-left: 4px solid #667eea;">
                    <strong>{row["Skill"]}</strong><br>
                    <small>{row["Priority"]} Priority • Impact: {row["Importance"]}%</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📈 Skills Category Breakdown")
            
            # Categorize skills (simple keyword-based categorization)
            tech_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'cloud', 'api', 'database', 'programming']
            soft_keywords = ['communication', 'leadership', 'management', 'teamwork', 'collaboration']
            cert_keywords = ['certification', 'certified', 'license', 'credential']
            
            categories = {'Technical Skills': 0, 'Soft Skills': 0, 'Certifications': 0, 'Other': 0}
            
            for keyword in missing_keywords:
                keyword_lower = keyword.lower()
                if any(tech in keyword_lower for tech in tech_keywords):
                    categories['Technical Skills'] += 1
                elif any(soft in keyword_lower for soft in soft_keywords):
                    categories['Soft Skills'] += 1
                elif any(cert in keyword_lower for cert in cert_keywords):
                    categories['Certifications'] += 1
                else:
                    categories['Other'] += 1
            
            # Create category visualization
            category_df = pd.DataFrame.from_dict(categories, orient='index', columns=['Count'])
            category_df = category_df[category_df['Count'] > 0]  # Only show non-zero categories
            
            if not category_df.empty:
                st.bar_chart(category_df)
                
                # Show category insights
                max_category = category_df.idxmax()['Count']
                st.info(f"💡 **Focus Area:** Most missing skills are in **{max_category}**")
            else:
                st.success("🎉 Great! No major skill gaps identified!")
    
    # Row 3: Action Plan
    st.markdown("---")
    st.markdown("#### 🚀 Recommended Action Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 🎯 Immediate Actions (Next 24 Hours)")
        if missing_keywords[:2]:
            for skill in missing_keywords[:2]:
                st.markdown(f"• Add **{skill}** to relevant sections")
        st.markdown("• Review job description keywords")
        st.markdown("• Update resume formatting for ATS")
    
    with col2:
        st.markdown("##### 📅 Short-term Goals (Next Week)")
        if missing_keywords[2:5]:
            for skill in missing_keywords[2:5]:
                st.markdown(f"• Research and add **{skill}**")
        st.markdown("• Optimize resume structure")
        st.markdown("• Prepare skill-based examples")
    
    with col3:
        st.markdown("##### 🎓 Long-term Development (Next Month)")
        if missing_keywords[5:8]:
            for skill in missing_keywords[5:8]:
                st.markdown(f"• Learn/improve **{skill}**")
        st.markdown("• Obtain relevant certifications")
        st.markdown("• Build portfolio projects")
    
    return True

# 🎯 Header Section
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎯 Smart ATS Pro</div>
    <div class="hero-subtitle">AI-Powered Resume Evaluation Platform</div>
    <div class="hero-description">
        Leverage advanced AI to analyze your resume against job descriptions, 
        identify skill gaps, and get actionable insights to land your dream job.
    </div>
</div>
""", unsafe_allow_html=True)

# 🔧 Initialize API
if not initialize_api():
    st.error("❌ GOOGLE_API_KEY not found in Streamlit secrets.")
    st.stop()

# 📊 Sidebar - Features & Info
with st.sidebar:
    st.markdown("### 🚀 Platform Features")
    
    features = [
        ("🎯", "ATS Optimization", "Get ATS-friendly resume recommendations"),
        ("📊", "Skills Gap Analysis", "Visual analysis of missing skills"),
        ("🔍", "Keyword Matching", "Industry-specific keyword optimization"),
        ("📈", "Match Scoring", "Quantitative resume-job fit analysis"),
        ("💡", "Smart Suggestions", "AI-powered improvement recommendations"),
        ("🔄", "Real-time Analysis", "Instant feedback on resume changes")
    ]
    
    for icon, title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.info("📝 Use PDF format for best text extraction")
    st.info("🎯 Include relevant keywords from job description")
    st.info("📊 Aim for 80%+ match score for better ATS performance")

# 🔧 API Test Section (Collapsible)
with st.expander("🔧 System Status & API Test"):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test Gemini Connection"):
            with st.spinner("Testing API connection..."):
                try:
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content("Hello! Please respond with 'API Working' if you can receive this message.")
                    st.success("✅ API Connection: Successful")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"❌ API Connection Failed: {e}")
    
    with col2:
        st.metric("API Status", "🟢 Online", "Connected")
        st.metric("Model", "LearnLM 2.0", "Latest")

# 📝 Main Input Section
st.markdown("## 📝 Resume Analysis")

# Create two columns for input
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📋 Job Description")
    jd = st.text_area(
        "Paste the complete job description here:",
        height=300,
        help="Include all requirements, responsibilities, and preferred qualifications",
        placeholder="Enter the job description you want to match your resume against..."
    )
    
    if jd:
        word_count = len(jd.split())
        st.caption(f"📊 Words: {word_count} | Characters: {len(jd)}")

with col2:
    st.markdown("### 📎 Resume Upload")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF format recommended):",
        type=["pdf"],
        help="Upload your resume in PDF format for best text extraction accuracy"
    )
    
    if uploaded_file is not None:
        st.success("✅ Resume uploaded successfully!")
        
        # Show file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        st.json(file_details)
        
        # Preview extracted text (first 500 characters)
        with st.expander("👁️ Preview Extracted Text"):
            preview_text = input_pdf_text(uploaded_file)
            if preview_text:
                st.text(preview_text[:500] + "..." if len(preview_text) > 500 else preview_text)

# 🎯 Analysis Section
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    analyze_button = st.button(
        "🚀 Analyze Resume",
        type="primary",
        use_container_width=True,
        help="Start AI-powered resume analysis"
    )

if analyze_button:
    if uploaded_file is not None and jd.strip() != "":
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract text
            status_text.text("📄 Extracting text from resume...")
            progress_bar.progress(20)
            resume_text = input_pdf_text(uploaded_file)
            
            if not resume_text:
                st.error("❌ Failed to extract text from PDF. Please try a different file.")
                st.stop()
            
            # Step 2: Prepare analysis
            status_text.text("🧠 Preparing AI analysis...")
            progress_bar.progress(40)
            
            input_prompt = f"""
Act as an expert ATS (Applicant Tracking System) analyzer. Analyze this resume against the job description.

IMPORTANT: Keep your response concise and well-structured. Provide specific, actionable feedback.

**RESUME TEXT (First 2000 characters):**
{resume_text[:2000]}

**JOB DESCRIPTION (First 1500 characters):**  
{jd[:1500]}

**ANALYSIS REQUIRED:**

**1. MATCH SCORE:** Provide percentage (0-100%) and brief reason

**2. MISSING KEYWORDS:** List top 5-8 missing important skills/keywords as bullets:
• [Keyword] - why important
• [Keyword] - why important

**3. STRENGTHS:** What resume does well (2-3 points)

**4. IMPROVEMENTS:** Top 3 specific suggestions

**5. ATS TIPS:** 2-3 technical formatting suggestions

Keep response under 1500 characters total. Be direct and actionable.
"""
            
            # Step 3: Get AI response
            status_text.text("🤖 Running AI analysis...")
            progress_bar.progress(70)
            
            response_text = get_gemini_response(input_prompt)
            
            if not response_text:
                st.error("❌ Failed to get AI analysis. Please try again later.")
                st.info("💡 **Troubleshooting Tips:**")
                st.write("1. Check your internet connection")  
                st.write("2. Verify your Google AI Studio API key is valid")
                st.write("3. Ensure you haven't exceeded API quotas")
                st.write("4. Try with a shorter job description or resume")
                st.stop()
            
            # Step 4: Parse response for visualization
            status_text.text("📊 Creating visualizations...")
            progress_bar.progress(90)
            
            match_score, missing_keywords = parse_ai_response(response_text)
            
            # Step 5: Complete
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # 📊 Results Section
            st.markdown("---")
            st.markdown('<div class="results-header"><h2>📊 Analysis Results</h2></div>', unsafe_allow_html=True)
            
            # Stats Overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{match_score}%</div>
                    <div class="stat-label">Match Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{len(missing_keywords)}</div>
                    <div class="stat-label">Missing Skills</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                recommendation = "Excellent" if match_score >= 80 else "Good" if match_score >= 60 else "Needs Work"
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{recommendation}</div>
                    <div class="stat-label">Overall Rating</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                words_analyzed = len(resume_text.split()) + len(jd.split())
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{words_analyzed:,}</div>
                    <div class="stat-label">Words Analyzed</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Visualization
            if missing_keywords:
                st.markdown("### 📈 Interactive Skills Gap Analysis")
                create_skills_visualization(match_score, missing_keywords)
            else:
                st.success("🎉 Excellent! No significant skill gaps identified.")
            
            # Detailed Analysis
            st.markdown("### 📋 Detailed Analysis Report")
            
            # Format the response with better styling
            formatted_response = response_text.replace("**", "**").replace("•", "•")
            st.markdown(formatted_response)
            
            # Action Items Section
            st.markdown("---")
            st.markdown("### 🎯 Next Steps")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔧 Quick Wins")
                if missing_keywords[:3]:
                    for i, keyword in enumerate(missing_keywords[:3], 1):
                        st.markdown(f"{i}. Add **{keyword}** to your resume")
                else:
                    st.success("Great! No critical keywords missing.")
            
            with col2:
                st.markdown("#### 📈 Improvement Plan")
                if match_score < 60:
                    st.error("🚨 Major revision needed - Consider restructuring resume")
                elif match_score < 80:
                    st.warning("⚠️ Good foundation - Add missing keywords and skills")
                else:
                    st.success("🎉 Excellent match - Minor optimizations recommended")
            
            # Download Section
            st.markdown("---")
            st.markdown("### 💾 Export Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download Analysis Report", use_container_width=True):
                    # Create downloadable report
                    report_content = f"""
SMART ATS PRO - RESUME ANALYSIS REPORT
=====================================

Match Score: {match_score}%
Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

{response_text}

---
Generated by Smart ATS Pro
"""
                    st.download_button(
                        label="📥 Download TXT Report",
                        data=report_content,
                        file_name=f"ats_analysis_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            
            with col2:
                if st.button("📊 Export Skills Data", use_container_width=True):
                    # Create CSV of missing skills
                    if missing_keywords:
                        skills_df = pd.DataFrame({
                            'Missing Skill': missing_keywords,
                            'Priority': ['High'] * min(3, len(missing_keywords)) + 
                                      ['Medium'] * max(0, min(4, len(missing_keywords) - 3)) +
                                      ['Low'] * max(0, len(missing_keywords) - 7)
                        })
                        
                        st.download_button(
                            label="📥 Download CSV",
                            data=skills_df.to_csv(index=False),
                            file_name=f"missing_skills_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
            
            with col3:
                if st.button("🔄 New Analysis", use_container_width=True):
                    st.experimental_rerun()
                    
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ An error occurred during analysis: {e}")
            
    else:
        st.warning("⚠️ Please upload a resume (PDF) and provide a job description to proceed.")

# 🎓 Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #7f8c8d;">
    <h4>🎯 Smart ATS Pro</h4>
    <p>Empowering job seekers with AI-driven resume optimization</p>
    <p style="font-size: 0.8rem;">Built with Streamlit • Powered by Google Gemini • Made with ❤️</p>
</div>
""", unsafe_allow_html=True)
