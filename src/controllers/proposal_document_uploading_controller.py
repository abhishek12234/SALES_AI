from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from DAL_files.proposal_document_uploading_dal import DocumentProcessingDAL
from schemas.users_schemas import UserBase
from dependencies import get_current_user
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router initialization
document_router = APIRouter()

# Initialize document processing service
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAEMlA-iE0Nu4sbhuM4TkGvMiuP8vUmIdg")
document_service = DocumentProcessingDAL(GEMINI_API_KEY)

# Pydantic models for request/response
class DocumentMetadata(BaseModel):
    extraction_method: str
    pages: int
    tables_detected: bool
    content_length: int
    has_content: bool

class DocumentProcessingResponse(BaseModel):
    filename: str
    processing_timestamp: str
    file_size_kb: float
    document_metadata: Optional[DocumentMetadata]
    summary: Optional[str]
    success: bool
    error: Optional[str]
    processing_time_seconds: Optional[float] = None

class DocumentValidationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    file_size_mb: Optional[float] = None
    file_type: Optional[str] = None

class BatchProcessingResponse(BaseModel):
    total_files: int
    successful_processes: int
    failed_processes: int
    results: List[DocumentProcessingResponse]
    batch_processing_time_seconds: float


@document_router.post("/upload", response_model=DocumentProcessingResponse)
async def upload_and_process_document(
    file: UploadFile = File(...),
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload and process a single document (PDF or DOCX).

    This endpoint:
    1. Validates the uploaded file
    2. Extracts content from the document
    3. Analyzes content using AI
    4. Returns a comprehensive summary

    Supported formats: PDF, DOCX, DOC
    Maximum file size: 10MB
    """
    start_time = datetime.now()

    try:
        logger.info(f"Document upload initiated by user {current_user.user_id}: {file.filename}")

        # Validate file
        if not file:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded"
            )

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File must have a filename"
            )

        # Read file content
        file_content = await file.read()

        # Create a file-like object for processing
        from io import BytesIO
        file_data = BytesIO(file_content)

        # Validate document
        validation_result = document_service.validate_document(file_data, file.filename)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=400,
                detail=validation_result['error']
            )

        # Reset file pointer for processing
        file_data.seek(0)

        # Process document
        result = document_service.process_document(file_data, file.filename)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        result['processing_time_seconds'] = round(processing_time, 2)

        # Convert to response model
        if result['success']:
            response = DocumentProcessingResponse(
                filename=result['filename'],
                processing_timestamp=result['processing_timestamp'],
                file_size_kb=result['file_size_kb'],
                document_metadata=DocumentMetadata(**result['document_metadata']),
                summary=result['summary'],
                success=result['success'],
                error=result['error'],
                processing_time_seconds=result['processing_time_seconds']
            )

            logger.info(f"Document processed successfully: {file.filename} in {processing_time:.2f}s")
            return response
        else:
            logger.error(f"Document processing failed: {file.filename} - {result['error']}")
            raise HTTPException(
                status_code=422,
                detail=f"Document processing failed: {result['error']}"
            )

    except HTTPException:
        raise
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Unexpected error processing document: {str(e)}"
        logger.error(f"{error_msg} - Processing time: {processing_time:.2f}s")

        raise HTTPException(
            status_code=500,
            detail=error_msg
        )



@document_router.post("/batch-upload", response_model=BatchProcessingResponse)
async def batch_upload_and_process_documents(
    files: List[UploadFile] = File(...),
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Upload and process multiple documents at once.

    This endpoint:
    1. Processes up to 5 documents simultaneously
    2. Validates each file individually
    3. Returns results for all files (successful and failed)
    4. Provides batch processing statistics

    Maximum files per batch: 5
    Supported formats: PDF, DOCX, DOC
    Maximum file size per file: 10MB
    """
    start_time = datetime.now()

    try:
        logger.info(f"Batch document upload initiated by user {current_user.user_id}: {len(files)} files")

        # Validate batch size
        if len(files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 files allowed per batch upload"
            )

        if len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="No files uploaded"
            )

        results = []
        successful_count = 0
        failed_count = 0

        # Process each file
        for file in files:
            file_start_time = datetime.now()

            try:
                if not file.filename:
                    result = {
                        'filename': 'unknown',
                        'processing_timestamp': datetime.now().isoformat(),
                        'file_size_kb': 0,
                        'document_metadata': None,
                        'summary': None,
                        'success': False,
                        'error': 'File must have a filename',
                        'processing_time_seconds': 0
                    }
                    failed_count += 1
                    results.append(DocumentProcessingResponse(**result))
                    continue

                # Read file content
                file_content = await file.read()

                # Create a file-like object for processing
                from io import BytesIO
                file_data = BytesIO(file_content)

                # Validate document
                validation_result = document_service.validate_document(file_data, file.filename)
                if not validation_result['valid']:
                    result = {
                        'filename': file.filename,
                        'processing_timestamp': datetime.now().isoformat(),
                        'file_size_kb': 0,
                        'document_metadata': None,
                        'summary': None,
                        'success': False,
                        'error': validation_result['error'],
                        'processing_time_seconds': (datetime.now() - file_start_time).total_seconds()
                    }
                    failed_count += 1
                    results.append(DocumentProcessingResponse(**result))
                    continue

                # Reset file pointer for processing
                file_data.seek(0)

                # Process document
                result = document_service.process_document(file_data, file.filename)

                # Calculate processing time for this file
                file_processing_time = (datetime.now() - file_start_time).total_seconds()
                result['processing_time_seconds'] = round(file_processing_time, 2)

                # Convert to response model
                if result['success']:
                    response = DocumentProcessingResponse(
                        filename=result['filename'],
                        processing_timestamp=result['processing_timestamp'],
                        file_size_kb=result['file_size_kb'],
                        document_metadata=DocumentMetadata(**result['document_metadata']),
                        summary=result['summary'],
                        success=result['success'],
                        error=result['error'],
                        processing_time_seconds=result['processing_time_seconds']
                    )
                    successful_count += 1
                    logger.info(f"Batch file processed: {file.filename}")
                else:
                    response = DocumentProcessingResponse(
                        filename=result['filename'],
                        processing_timestamp=result['processing_timestamp'],
                        file_size_kb=0,
                        document_metadata=None,
                        summary=result['summary'],
                        success=result['success'],
                        error=result['error'],
                        processing_time_seconds=result['processing_time_seconds']
                    )
                    failed_count += 1
                    logger.error(f"Batch file failed: {file.filename} - {result['error']}")

                results.append(response)

            except Exception as e:
                file_processing_time = (datetime.now() - file_start_time).total_seconds()
                error_msg = f"Error processing file: {str(e)}"

                result = {
                    'filename': file.filename if file.filename else 'unknown',
                    'processing_timestamp': datetime.now().isoformat(),
                    'file_size_kb': 0,
                    'document_metadata': None,
                    'summary': None,
                    'success': False,
                    'error': error_msg,
                    'processing_time_seconds': round(file_processing_time, 2)
                }
                failed_count += 1
                results.append(DocumentProcessingResponse(**result))
                logger.error(f"Exception processing batch file {file.filename}: {error_msg}")

        # Calculate total processing time
        total_processing_time = (datetime.now() - start_time).total_seconds()

        # Create batch response
        batch_response = BatchProcessingResponse(
            total_files=len(files),
            successful_processes=successful_count,
            failed_processes=failed_count,
            results=results,
            batch_processing_time_seconds=round(total_processing_time, 2)
        )

        logger.info(f"Batch processing completed: {successful_count}/{len(files)} successful in {total_processing_time:.2f}s")
        return batch_response

    except HTTPException:
        raise
    except Exception as e:
        total_processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Unexpected error in batch processing: {str(e)}"
        logger.error(f"{error_msg} - Total time: {total_processing_time:.2f}s")

        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


