import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

load_dotenv()  # load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Database of Company Job Descriptions
company_database = {
    "Company1": "We are looking for a skilled software engineer with expertise in Python and Django...",
    "Company2": "Join our data science team and work on exciting projects involving machine learning and data analysis...",
    # We can add more companies and job descriptions
}

# Gemini Pro Response
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to Match Resume with Job Descriptions using Sentence-Transformers
def match_resume_to_job(resume_text):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    resume_embedding = model.encode(resume_text)

    matched_companies = []
    for company, job_description in company_database.items():
        jd_embedding = model.encode(job_description)
        similarity_score = util.pytorch_cos_sim(resume_embedding, jd_embedding)[0][0].item()
        matched_companies.append({"company": company, "similarity_score": similarity_score * 100})

    return matched_companies

# Function to Recommend Resume Improvements (Simple Keyword Matching)
def recommend_resume_improvements(resume_text):
    keywords_to_include = ["python", "data science", "machine learning"]  # Replace with your relevant keywords

    missing_keywords = [keyword for keyword in keywords_to_include if keyword.lower() not in resume_text.lower()]
    return missing_keywords

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")
submit = st.button("Submit")

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analyst,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive, and you should provide 
the best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

if submit:
    if uploaded_file is not None:
        # Extract text from PDF
        text = input_pdf_text(uploaded_file)

        # Match resume with job descriptions
        matched_companies = match_resume_to_job(text)
        st.subheader("Suitable Companies:")
        for match in matched_companies:
            st.write(f"{match['company']}: {match['similarity_score']:.2f}% match")

        # Display company with the highest similarity
        if matched_companies:
            best_match = max(matched_companies, key=lambda x: x['similarity_score'])
            st.subheader(f"Recommended Company: {best_match['company']} ({best_match['similarity_score']:.2f}% match)")

        # Recommend resume improvements
        recommended_improvements = recommend_resume_improvements(text)
        st.subheader("Resume Recommendations:")
        if recommended_improvements:
            st.write("Add the following keywords to improve your resume:")
            for improvement in recommended_improvements:
                st.write(f"- {improvement}")
        else:
            st.write("Your resume is well-matched with the required keywords.")

        # Generate response using Gemini Pro
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))
        st.subheader("Gemini Pro Response:")
        st.write(response)
