import streamlit as st
from google.generativeai import genai
import pdf2image as pdf
from dotenv import load_dotenv

load_dotenv()  # Load all environment variables

# Check if the API key is available
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("Google API key not found. Please check your configuration.")
    st.stop()

genai.configure(api_key=google_api_key)

# Gemini Pro Response
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    try:
        with open(uploaded_file, 'rb') as file:
            reader = pdf.PdfReader(file)
            text = "".join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        st.stop()

# Prompt Template
input_prompt = f"""
Hey! Act like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive, and you should provide 
the best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.
resume:{{text}}
description:{{jd}}

I want the response in one single string having the structure
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        input_prompt_formatted = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(input_prompt_formatted)
        st.subheader(response)

