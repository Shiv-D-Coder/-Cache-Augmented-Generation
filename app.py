import streamlit as st
import asyncio
import PyPDF2
import docx
from extract_docx import ExtractDocx
from groq import AsyncGroq
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Setup ---
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ''.join([page.extract_text() for page in reader.pages])

# def extract_text_from_docx(docx_path):
#     doc = docx.Document(docx_path)
#     full_text = []
#     for para in doc.paragraphs:
#         full_text.append(para.text)
#     return '\n'.join(full_text)

from extract_docx import ExtractDocx

def extract_text_from_docx(docx_path):
    ed = ExtractDocx(docx_path)
    return ed.extract_text()

def load_knowledge_cache(file_path, max_length=6000):
    file_extension = file_path.split('.')[-1].lower()
    try:
        if file_extension == 'pdf':
            return extract_text_from_pdf(file_path)[:max_length]
        elif file_extension == 'docx':
            return extract_text_from_docx(file_path)[:max_length]
        else:
            st.error("Unsupported file type. Please upload a PDF or DOCX file.")
            return None
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        return None

# --- Constants ---
MODEL_OPTIONS = {
    "qwen-qwq-32b": "qwen-qwq-32b",
    "llama-3.1-8b-instant": "llama-3.1-8b-instant",
    "gemma2-9b-it": "gemma2-9b-it",
}

# --- Initialize State ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.title("CAG - Cache Augmented Generation")

# --- Sidebar ---
with st.sidebar:
    st.header("CAG Settings")

    api_key = st.text_input("Groq API Key", type="password")
    if not api_key:
        st.info("Please enter your Groq API key to continue.")
        st.stop()

    model_name = st.selectbox("Choose Model", options=list(MODEL_OPTIONS.keys()), index=0)

    uploaded_file = st.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])
    if uploaded_file is None:
        st.info("Please upload a PDF or DOCX file to proceed.")
        st.stop()
    
    st.download_button(
        label="Download Chat History",
        data=json.dumps({"model": st.session_state["chat_history"]}, indent=4),
        file_name="history.json",
        mime="application/json",
    )

# --- Groq API Functions ---
async def generate_response_async(prompt, groq_api_key, model):
    async with AsyncGroq(api_key=groq_api_key) as client:
        chat_completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content.strip()

async def augmented_generation(question: str, knowledge_cache: str, groq_api_key: str, model: str) -> str:
    prompt = f"""KNOWLEDGE BASE:
{knowledge_cache}

QUESTION: {question}
ANSWER:"""
    
    response = await generate_response_async(prompt, groq_api_key, model)
    return response

# --- Main Chat Interface ---
# st.title("CAG - Cache Augmented Generation")

# Load or initialize knowledge cache once
if "knowledge_cache" not in st.session_state:
    with st.spinner('Loading knowledge base...'):
        try:
            # Use the uploaded file name
            st.session_state["knowledge_cache"] = load_knowledge_cache(uploaded_file.name)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

# Display chat messages from history
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question:"):
    # Add user message to chat history
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get model response
    start_time = time.time()
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            full_response = asyncio.run(augmented_generation(prompt, st.session_state["knowledge_cache"], api_key, MODEL_OPTIONS[model_name]))
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            full_response = "Sorry, an error occurred while processing your request."
        
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    end_time = time.time()
    response_time = end_time - start_time
    st.write(f"Response Time: {response_time:.2f} seconds")

    # Add assistant response to chat history
    st.session_state["chat_history"].append({"role": "assistant", "content": full_response})
