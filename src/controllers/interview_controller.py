from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from io import BytesIO
import os

from DAL_files.interview_dal import InterviewService

interview_router = APIRouter()
interview_service = InterviewService()

@interview_router.post("/get-persona-behavior")
async def upload_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        return JSONResponse(status_code=400, content={"error": "Invalid file format. Please upload a .docx file."})

    file_bytes = await file.read()
    file_stream = BytesIO(file_bytes)
    transcript = interview_service.extract_text_from_docx(file_stream)
    if transcript.startswith("Error") or not transcript:
        return JSONResponse(status_code=400, content={"error": transcript or "No text content found in the file."})

   
    persona = await interview_service.generate_persona(transcript)
    return {"persona": persona} 