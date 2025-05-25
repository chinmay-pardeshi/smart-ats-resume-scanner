# from dotenv import load_dotenv

# load_dotenv()

# import base64
# import streamlit as st
# import os
# import io
# from PIL import Image 
# import pdf2image
# import google.generativeai as genai

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_gemini_response(input,pdf_cotent,prompt):
#     model=genai.GenerativeModel('gemini-1.5-pro')
# # learnlm-2.0-flash-experimental    
#     response=model.generate_content([input,pdf_content[0],prompt])
#     return response.text

# def input_pdf_setup(uploaded_file):
#     if uploaded_file is not None:
#         ## Convert the PDF to image
#         images=pdf2image.convert_from_bytes(uploaded_file.read())

#         first_page=images[0]

#         # Convert to bytes
#         img_byte_arr = io.BytesIO()
#         first_page.save(img_byte_arr, format='JPEG')
#         img_byte_arr = img_byte_arr.getvalue()

#         pdf_parts = [
#             {
#                 "mime_type": "image/jpeg",
#                 "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
#             }
#         ]
#         return pdf_parts
#     else:
#         raise FileNotFoundError("No file uploaded")


# ## Streamlit App

# st.set_page_config(page_title="ATS Resume EXpert")
# st.header("ATS Tracking System")
# input_text=st.text_area("Job Description: ",key="input")
# uploaded_file=st.file_uploader("Upload your resume(PDF)...",type=["pdf"])


# if uploaded_file is not None:
#     st.write("PDF Uploaded Successfully")


# submit1 = st.button("Tell Me About the Resume")

# submit2 = st.button("How Can I Improvise my Skills")

# submit3 = st.button("how Can I improve my Skills")

# submit4 = st.button("Percentage match")

# input_prompt1 = """
#  You are an experienced HR With Tech Experience in the filed of any one job role form Data Science, Full stack Web development,
#  Big Data Engineering,DEVOPS, Data Analyst, your task is to review the provided resume against the job 
#  description for these profiles. Please share your professional evaluation on whether the candidate's 
#  profile aligns with Highlight the strengths and weaknesses of the applicant in relation to the specified 
#  job requirements.
# """
# # input_prompt2 = """
# # You are an experienced HR professional with a strong technical background in Data Science, Full Stack Web Development, 
# # Big Data Engineering, DevOps, and Data Analysis. Your task is to carefully review the uploaded resume in relation to 
# # the provided job description. Provide a detailed evaluation of how well the candidate’s profile aligns with the job 
# # requirements. Highlight specific strengths, technical skills, and relevant experience. Also, point out any gaps, 
# # missing skills, or areas for improvement that could enhance the candidate’s chances of securing the role.
# # """


# input_prompt3 = """
# You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of any one job role Data Science, Full stack Web development,
# Big Data Engineering,DEVOPS, Data Analyst deep ATS functionality, your task is to evaluate the resume against the 
# provided job description. give me the percentage of match if the resume matches the job description. First the
# output should come as percentage and then keywords missing and last final thoughts.
# """

# # input_prompt4 = """
# # You are an experienced HR professional with expertise in technical hiring for roles such as Data Scientist, Full Stack Developer, 
# # Big Data Engineer, DevOps Engineer, and Data Analyst. Analyze the candidate’s resume against the provided job description. 
# # Offer a comprehensive review that includes how well the resume matches the role, the strengths of the profile, and any 
# # technical or domain-specific gaps. Provide suggestions for improving the resume to better meet the expectations of the role.
# # """


# if submit1:
#     if uploaded_file is not None:
#         pdf_content=input_pdf_setup(uploaded_file)
#         response=get_gemini_response(input_prompt1,pdf_content,input_text)
#         st.subheader("The Repsonse is")
#         st.write(response)
#     else:
#         st.write("Please uplaod the resume")

# elif submit3:
#     if uploaded_file is not None:
#         pdf_content=input_pdf_setup(uploaded_file)
#         response=get_gemini_response(input_prompt3,pdf_content,input_text)
#         st.subheader("The Repsonse is")
#         st.write(response)
#     else:
#         st.write("Please uplaod the resume")




# # from dotenv import load_dotenv

# # load_dotenv()

# # import base64
# # import streamlit as st
# # import os
# # import io
# # from PIL import Image 
# # import pdf2image
# # import google.generativeai as genai

# # genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # def get_gemini_response(input, pdf_content, prompt):
# #     # Fixed model name - removed extra spaces
# #     model = genai.GenerativeModel('models/learnlm-2.0-flash-experimental')
# #     response = model.generate_content([input, pdf_content[0], prompt])
# #     return response.text

# # def input_pdf_setup(uploaded_file):
# #     if uploaded_file is not None:
# #         try:
# #             # Convert the PDF to image
# #             images = pdf2image.convert_from_bytes(uploaded_file.read())

# #             first_page = images[0]

# #             # Convert to bytes
# #             img_byte_arr = io.BytesIO()
# #             first_page.save(img_byte_arr, format='JPEG')
# #             img_byte_arr = img_byte_arr.getvalue()

# #             pdf_parts = [
# #                 {
# #                     "mime_type": "image/jpeg",
# #                     "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
# #                 }
# #             ]
# #             return pdf_parts

# #         except pdf2image.exceptions.PDFInfoNotInstalledError:
# #             st.error("Poppler is not installed or not added to PATH. Please install it from:\n"
# #                      "https://github.com/oschwartz10612/poppler-windows/releases\n"
# #                      "Then add 'C:\\poppler\\Library\\bin' to your PATH environment variable.")
# #             return None
# #         except Exception as e:
# #             st.error(f"An unexpected error occurred while processing the PDF: {e}")
# #             return None
# #     else:
# #         st.warning("No file uploaded.")
# #         return None


# # ## Streamlit App
# # st.set_page_config(page_title="ATS Resume Expert")
# # st.header("ATS Tracking System")
# # input_text = st.text_area("Job Description: ", key="input")
# # uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# # if uploaded_file is not None:
# #     st.write("PDF Uploaded Successfully")

# # # Input prompts
# # input_prompt1 = """
# #  You are an experienced HR With Tech Experience in the field of Data Science, Full stack Web development,
# #  Big Data Engineering, DEVOPS, Data Analyst, your task is to review the provided resume against the job 
# #  description for these profiles. Please share your professional evaluation on whether the candidate's 
# #  profile aligns with. Highlight the strengths and weaknesses of the applicant in relation to the specified 
# #  job requirements.
# # """

# # # input_prompt2 = """
# # # You are an experienced HR professional with a strong technical background in Data Science, Full Stack Web Development, 
# # # Big Data Engineering, DevOps, and Data Analysis. Your task is to carefully review the uploaded resume in relation to 
# # # the provided job description. Provide a detailed evaluation of how well the candidate's profile aligns with the job 
# # # requirements. Highlight specific strengths, technical skills, and relevant experience. Also, point out any gaps, 
# # # missing skills, or areas for improvement that could enhance the candidate's chances of securing the role.
# # # """

# # input_prompt3 = """
# # You are an experienced HR professional with expertise in technical hiring for roles such as Data Scientist, Full Stack Developer, 
# # Big Data Engineer, DevOps Engineer, and Data Analyst. Analyze the candidate's resume against the provided job description. 
# # Offer a comprehensive review that includes how well the resume matches the role, the strengths of the profile, and any 
# # technical or domain-specific gaps. Provide suggestions for improving the resume to better meet the expectations of the role.
# # """

# # # input_prompt4 = """
# # # You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
# # # your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
# # # the job description. First the output should come as percentage and then keywords missing and last final thoughts.
# # # """

# # # Define buttons with clearer purposes
# # col1, col2 = st.columns(2)
# # with col1:
# #     submit1 = st.button("Resume Analysis")
# #     submit3 = st.button("Skills Improvement")
# # with col2:
# #     submit2 = st.button("Job Match Evaluation")
# #     submit4 = st.button("ATS Match Percentage")

# # # Handle button clicks
# # if submit1:
# #     if uploaded_file is not None:
# #         pdf_content = input_pdf_setup(uploaded_file)
# #         if pdf_content:
# #             response = get_gemini_response(input_prompt1, pdf_content, input_text)
# #             st.subheader("Resume Analysis")
# #             st.write(response)
# #     else:
# #         st.error("Please upload your resume")

# # elif submit2:
# #     if uploaded_file is not None:
# #         pdf_content = input_pdf_setup(uploaded_file)
# #         if pdf_content:
# #             response = get_gemini_response(input_prompt2, pdf_content, input_text)
# #             st.subheader("Job Match Evaluation")
# #             st.write(response)
# #     else:
# #         st.error("Please upload your resume")

# # elif submit3:
# #     if uploaded_file is not None:
# #         pdf_content = input_pdf_setup(uploaded_file)
# #         if pdf_content:
# #             response = get_gemini_response(input_prompt3, pdf_content, input_text)
# #             st.subheader("Skills Improvement Suggestions")
# #             st.write(response)
# #     else:
# #         st.error("Please upload your resume")

# # elif submit4:
# #     if uploaded_file is not None:
# #         pdf_content = input_pdf_setup(uploaded_file)
# #         if pdf_content:
# #             response = get_gemini_response(input_prompt4, pdf_content, input_text)
# #             st.subheader("ATS Match Percentage")
# #             st.write(response)
# #     else:
# #         st.error("Please upload your resume")
