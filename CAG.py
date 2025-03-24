# import os
# import asyncio
# import PyPDF2
# from groq import AsyncGroq
# from dotenv import load_dotenv
# from colorama import Fore, Style, init

# # Initialize colorama
# init(autoreset=True)

# # Load environment variables
# load_dotenv()

# # Step 1: Extract Text from PDF
# def extract_text_from_pdf(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         return ''.join([page.extract_text() for page in reader.pages])

# # Step 2: Initialize Knowledge Cache
# extinct_animals_pdf = "Extinct Animals.pdf"
# knowledge_cache = extract_text_from_pdf(extinct_animals_pdf)[:6000]  # Truncate to fit context limit

# # Step 3: Set Up Groq API Client
# GROQ_API_KEY = os.environ["GROQ_API_KEY"] 

# async def generate_response_async(prompt):
#     async with AsyncGroq(api_key=GROQ_API_KEY) as client:
#         chat_completion = await client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama-3.1-8b-instant",
#             max_tokens=1024,
#         )
#         return chat_completion.choices[0].message.content.strip()

# # Step 4: Implement CAG Logic
# async def extinct_animal_query(question: str) -> str:
#     prompt = f"""EXTINCT ANIMAL KNOWLEDGE BASE:
# {knowledge_cache}

# QUESTION: {question}
# ANSWER:"""
    
#     response = await generate_response_async(prompt)
#     return response

# # Step 5: Infinite Loop for Command Line Interaction
# if __name__ == "__main__":
#     print(Fore.GREEN + "Welcome to the Extinct Animal Knowledge Base!")
#     print(Fore.YELLOW + "Type your questions below or type 'exit' to quit.\n")

#     while True:
#         question = input(Fore.CYAN + "Your Question: ").strip()
        
#         if question.lower() == "exit":
#             print(Fore.RED + "Exiting the program. Goodbye!")
#             break
        
#         try:
#             response = asyncio.run(extinct_animal_query(question))
#             print(Fore.GREEN + "\nAnswer:\n" + Fore.WHITE + response + "\n")
#         except Exception as e:
#             print(Fore.RED + f"An error occurred: {str(e)}")
import os
import asyncio
import PyPDF2
from groq import AsyncGroq
from dotenv import load_dotenv
from colorama import Fore, Style, init
import json
import time

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# Step 1: Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ''.join([page.extract_text() for page in reader.pages])

# Step 2: Initialize Knowledge Cache
extinct_animals_pdf = "Extinct Animals.pdf"
knowledge_cache = extract_text_from_pdf(extinct_animals_pdf)[:6000]  # Truncate to fit context limit

# Step 3: Set Up Groq API Client
GROQ_API_KEY = os.environ["GROQ_API_KEY"] 

async def generate_response_async(prompt):
    async with AsyncGroq(api_key=GROQ_API_KEY) as client:
        chat_completion = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content.strip()

# Step 4: Implement CAG Logic
async def extinct_animal_query(question: str) -> str:
    prompt = f"""EXTINCT ANIMAL KNOWLEDGE BASE:
{knowledge_cache}

QUESTION: {question}
ANSWER:"""
    
    response = await generate_response_async(prompt)
    return response

# Step 5: Save Interaction History to JSON
def save_to_history(question, answer):
    history_file = 'history.json'
    
    # Load existing history if it exists
    if os.path.exists(history_file):
        with open(history_file, 'r') as file:
            history = json.load(file)
    else:
        history = {"model": []}
    
    # Append new question and answer
    history["model"].append({"question": question, "answer": answer})
    
    # Save back to JSON file
    with open(history_file, 'w') as file:
        json.dump(history, file, indent=4)

# Step 6: Infinite Loop for Command Line Interaction
if __name__ == "__main__":
    print(Fore.GREEN + "Welcome to the Extinct Animal Knowledge Base!")
    print(Fore.YELLOW + "Type your questions below or type 'exit' to quit.\n")

    while True:
        question = input(Fore.CYAN + "Your Question: ").strip()
        
        if question.lower() == "exit":
            print(Fore.RED + "Exiting the program. Goodbye!")
            break
        
        try:
            start_time = time.time()  # Start timing
            
            response = asyncio.run(extinct_animal_query(question))
            
            end_time = time.time()  # End timing
            response_time = end_time - start_time
            
            print(Fore.GREEN + "\nAnswer:\n" + Fore.WHITE + response + "\n")
            print(Fore.YELLOW + f"Response Time: {response_time:.2f} seconds")
            
            # Save question and answer to history.json
            save_to_history(question, response)
        
        except Exception as e:
            print(Fore.RED + f"An error occurred: {str(e)}")
