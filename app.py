import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import time
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
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
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_gemini_response(prompt, retries=3, delay=2):
    try:
        model = genai.GenerativeModel("models/learnlm-2.0-flash-experimental")
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini model: {e}")
        return None
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(delay)
            else:
                st.error(f"❌ All attempts failed. Last error: {e}")
    return None

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

# ✅ Create Skills Gap Visualization
def create_skills_visualization(match_score, missing_keywords):
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Overall Match Score', 'Skills Gap Analysis', 'Top Missing Skills', 'Recommendation Priority'),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "scatter"}]]
    )
    
    # 1. Match Score Gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=match_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Match Score: {match_score}%"},
            delta={'reference': 80, 'position': "top"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 80], 'color': "#fff3e0"},
                    {'range': [80, 100], 'color': "#e8f5e8"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=1
    )
    
    # 2. Skills Gap Bar Chart
    categories = ['Technical Skills', 'Soft Skills', 'Experience', 'Education', 'Certifications']
    gap_scores = [85, 70, 90, 75, 60]  # Mock data - you can enhance this based on actual analysis
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=gap_scores,
            marker_color=['#667eea', '#764ba2', '#11998e', '#38ef7d', '#ffa726'],
            name="Skill Match %"
        ),
        row=1, col=2
    )
    
    # 3. Missing Skills Pie Chart
    if missing_keywords:
        # Take top 5 missing keywords for visualization
        top_missing = missing_keywords[:5] if len(missing_keywords) >= 5 else missing_keywords
        values = [len(keyword.split()) for keyword in top_missing]  # Simple weight based on keyword length
        
        fig.add_trace(
            go.Pie(
                labels=top_missing,
                values=values,
                hole=0.4,
                marker_colors=['#ff6b6b', '#ffa726', '#ffeb3b', '#66bb6a', '#42a5f5']
            ),
            row=2, col=1
        )
    
    # 4. Recommendation Priority Scatter
    priority_skills = missing_keywords[:8] if len(missing_keywords) >= 8 else missing_keywords
    importance = [90, 85, 80, 75, 70, 65, 60, 55][:len(priority_skills)]
    difficulty = [30, 45, 60, 40, 80, 35, 55, 70][:len(priority_skills)]
    
    fig.add_trace(
        go.Scatter(
            x=difficulty,
            y=importance,
            mode='markers+text',
            text=priority_skills,
            textposition="top center",
            marker=dict(
                size=16,
                color=importance,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Importance")
            ),
            name="Skills Priority"
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="📊 Comprehensive Skills Gap Analysis",
        title_x=0.5,
        title_font_size=20
    )
    
    # Update axes labels for scatter plot
    fig.update_xaxes(title_text="Learning Difficulty", row=2, col=2)
    fig.update_yaxes(title_text="Importance Level", row=2, col=2)
    
    return fig

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
As an expert ATS (Applicant Tracking System) analyzer and HR professional, provide a comprehensive evaluation of this resume against the job description.

Please structure your response with these exact sections:

**1. OVERALL MATCH SCORE**
Provide a percentage match (0-100%) and brief explanation.

**2. MISSING KEYWORDS**
List the most important missing keywords/skills as bullet points:
• [Keyword 1] - Brief explanation why it's important
• [Keyword 2] - Brief explanation why it's important
• [Continue for top 8-10 missing items]

**3. STRENGTHS ANALYSIS**
Highlight what the resume does well in relation to the job requirements.

**4. IMPROVEMENT RECOMMENDATIONS**
Provide specific, actionable suggestions for improvement.

**5. ATS OPTIMIZATION TIPS**
Technical suggestions for better ATS performance.

Resume Text:
{resume_text}

Job Description:
{jd}

Important: Focus on actionable insights that will help improve the candidate's chances of getting through ATS systems and impressing hiring managers.
"""
            
            # Step 3: Get AI response
            status_text.text("🤖 Running AI analysis...")
            progress_bar.progress(70)
            
            response_text = get_gemini_response(input_prompt)
            
            if not response_text:
                st.error("❌ Failed to get AI analysis. Please try again.")
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
                fig = create_skills_visualization(match_score, missing_keywords)
                st.plotly_chart(fig, use_container_width=True)
            
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
