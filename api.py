from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import io

app = FastAPI()
model = genai.GenerativeModel("gemini-pro")
GOOGLE_API_KEY = "Your_API_KEYY"
genai.configure(api_key=GOOGLE_API_KEY)
chat = model.start_chat(history=[])

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://miniproject-one.vercel.app", 
    "https://api-backend-git-main-snathsujiths-projects.vercel.app/api/getGeminiResponse",
    "http://localhost:8000/api/getGeminiResponse",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResponseModel(BaseModel):
    result: str

def get_gemini_response(text: str) -> str:
    try:
        response = chat.send_message(text)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        raise HTTPException(status_code=500, detail="Error getting Gemini response")

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        doc = fitz.open(stream=pdf_file.file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Error extracting text from PDF")

@app.post("/api/getPdfSummary", response_model=ResponseModel)
async def api_get_pdf_summary(file: UploadFile = File(...)):
    try:
        pdf_text = extract_text_from_pdf(file)
        summary = get_gemini_response(pdf_text)
        return ResponseModel(result=summary)
    except Exception as e:
        print(f"Error in /api/getPdfSummary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
