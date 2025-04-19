from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
import fitz
import torch
from transformers import pipeline
import tempfile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.models.quiz import generate_multiple_mcqs
import re 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "facebook/bart-large-cnn"  
summarizer = pipeline("summarization", model=model_name, device=0 if device == "cuda" else -1)

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")  
    return text

def chunk_text(text, chunk_size=2000):
    chunks = []
    while len(text) > chunk_size:
        idx = text[:chunk_size].rfind(".")
        if idx == -1:
            idx = chunk_size
        chunks.append(text[:idx + 1])
        text = text[idx + 1:].strip()
    if text:
        chunks.append(text)
    return chunks

def hierarchical_summarization(text):
    chunks = chunk_text(text)
    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        if chunk.strip():
            input_length = len(chunk.split())
            max_length = min(300, input_length // 2 + 50)
            max_length = min(max_length, 500)  
            if input_length < 10:
                max_length = min(50, input_length)

            try:
                summary = summarizer(chunk, max_length=max_length, min_length=50, do_sample=False)
                chunk_summaries.append(summary[0]['summary_text'])
            except Exception as e:
                print(f"Error summarizing chunk {i + 1}: {e}")

    return " ".join(chunk_summaries)
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        print("Request received!")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name
        extracted_text = extract_pdf_text(temp_path)
        print(f"Extracted Text: {extracted_text[:500]}")  

        if not extracted_text.strip():
            return {"error": "No text found in PDF"}

        summary = hierarchical_summarization(extracted_text)

        os.remove(temp_path)

        return {"summary": summary}
    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": f"Failed to process PDF: {e}"}

class MCQRequest(BaseModel):
    paragraph: str
    num_questions: int = 5

@app.post("/generate_mcqs/")
async def generate_mcqs(request: MCQRequest):
    try:
        paragraph = request.paragraph
        num_questions = request.num_questions * 2  
        print(f"Received paragraph: {paragraph}")
        print(f"Number of MCQs requested: {num_questions}")

        raw_mcqs = generate_multiple_mcqs(paragraph, num_questions=num_questions)
        mcqs = [parse_mcqs(mcq) for mcq in raw_mcqs]
        valid_mcqs = [mcq for mcq in mcqs if mcq and len(mcq["options"]) >= 4]
        
        print(f"Generated {len(valid_mcqs)} valid MCQs from {len(raw_mcqs)} raw")
        
        if len(valid_mcqs) < request.num_questions:
            additional_needed = request.num_questions - len(valid_mcqs)
            print(f"Need {additional_needed} more MCQs. Generating...")
            additional_raw = generate_multiple_mcqs(paragraph, num_questions=additional_needed*3)
            additional_mcqs = [parse_mcqs_alternative(mcq) for mcq in additional_raw]
            additional_valid = [mcq for mcq in additional_mcqs if mcq and len(mcq["options"]) >= 4]
            valid_mcqs.extend(additional_valid)
        
        return {"mcqs": valid_mcqs[:request.num_questions]}
    except Exception as e:
        print(f"Exception in generate_mcqs: {str(e)}")
        return {"error": f"Failed to generate MCQs: {e}"}

def parse_mcqs(raw_mcq: str):
    pattern = r"""
        Question:\s*(?P<question>.+?)\n
        A\)\s*(?P<optionA>.+?)\n
        B\)\s*(?P<optionB>.+?)\n
        C\)\s*(?P<optionC>.+?)\n
        D\)\s*(?P<optionD>.+?)\n
        Correct\s+Answer:\s*[A-D]\)\s*(?P<correct>.+)
    """.strip()
    
    match = re.search(pattern, raw_mcq, re.DOTALL | re.IGNORECASE | re.VERBOSE)
    
    if not match:
        return parse_mcqs_alternative(raw_mcq)
        
    return {
        "question": match.group("question").strip(),
        "options": [
            match.group("optionA").strip(),
            match.group("optionB").strip(),
            match.group("optionC").strip(),
            match.group("optionD").strip()
        ],
        "correct_answer": match.group("correct").strip()
    }

def parse_mcqs_alternative(raw_mcq: str):
    try:
        # Extract the question
        question_match = re.search(r"(?:Question:|^\d+\.?)\s*(.+?)(?:\n|$)", raw_mcq, re.IGNORECASE | re.DOTALL)
        if not question_match:
            return None
            
        question = question_match.group(1).strip()
        
        # Extract options
        options_pattern = r"(?:[A-D][\.\):])\s*(.+?)(?=\n[A-D][\.\):]|\n(?:Correct|Answer)|$)"
        options_matches = re.finditer(options_pattern, raw_mcq, re.DOTALL)
        options = [match.group(1).strip() for match in options_matches]
        
        if len(options) < 4:
            return None
            
        # Extract correct answer
        correct_pattern = r"(?:Correct\s*Answer|Answer)(?:\s*is)?(?:\s*:)?\s*[A-D][\.\):]?\s*(.+?)(?:\n|$)"
        correct_match = re.search(correct_pattern, raw_mcq, re.IGNORECASE | re.DOTALL)
        
        if not correct_match:
            # Try to find which option (A, B, C, D) is marked as correct
            answer_letter_match = re.search(r"(?:Correct\s*Answer|Answer)(?:\s*is)?(?:\s*:)?\s*([A-D])", raw_mcq, re.IGNORECASE)
            if answer_letter_match:
                letter_idx = ord(answer_letter_match.group(1).upper()) - ord('A')
                if 0 <= letter_idx < len(options):
                    correct_answer = options[letter_idx]
                else:
                    return None
            else:
                return None
        else:
            correct_answer = correct_match.group(1).strip()
            
            # Verify the correct answer is one of the options
            if correct_answer not in options:
                for option in options:
                    if option.lower() == correct_answer.lower():
                        correct_answer = option
                        break
                    elif option in correct_answer or correct_answer in option:
                        correct_answer = option
                        break
                else:
                    # If still not found, use the first option as a fallback
                    correct_answer = options[0]
        
        return {
            "question": question,
            "options": options[:4],  # Ensure exactly 4 options
            "correct_answer": correct_answer
        }
    except Exception as e:
        print(f"Error in parse_mcqs_alternative: {str(e)}")
        return None