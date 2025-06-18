from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from DAL_files.ai_persona_dal import AIPersonaDAL
from schemas.ai_personas_schemas import (
    AIPersonaCreate,
    AIPersonaUpdate,
    AIPersonaResponse
)
from database import get_session
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum
from sqlalchemy.exc import IntegrityError
import logging
import os
import base64
from appwrite_store import add_file, get_file_url


logger = logging.getLogger("ai_persona")

# Create different role checkers for different access levels
admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

ai_persona_router = APIRouter()
ai_persona_service = AIPersonaDAL()

@ai_persona_router.post("/", response_model=AIPersonaResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_ai_persona(
    persona_data: AIPersonaCreate,
    session: AsyncSession = Depends(get_session)
):
    try:    
        new_persona = await ai_persona_service.create_ai_persona(persona_data, session)
        return new_persona
    except IntegrityError as e:
        logger.exception("Integrity error while creating ai persona")
        
        if "Duplicate entry" in str(e.orig):
            raise HTTPException(status_code=400, detail="AI Persona with this name already exists.")
        elif "cannot be null" in str(e.orig):
            raise HTTPException(status_code=400, detail="A required field is missing.")
        elif "foreign key constraint fails" in str(e.orig):
            raise HTTPException(status_code=400, detail="Invalid reference to another table.")
        else:
            raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        logger.exception("Failed to create ai persona")
        raise HTTPException(status_code=500, detail="Internal server error")

@ai_persona_router.get("/{persona_id}", response_model=AIPersonaResponse, status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_ai_persona(
    persona_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get an AI Persona by ID
    """
    persona = await ai_persona_service.get_ai_persona_by_id(persona_id, session)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Persona not found"
        )
    return persona

@ai_persona_router.get("/", response_model=List[AIPersonaResponse], status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_all_ai_personas(
    session: AsyncSession = Depends(get_session)
):
    """
    Get all AI Personas, including their profile picture as a base64 string if available.
    """
    personas = await ai_persona_service.get_all_ai_personas(session)

    return personas

@ai_persona_router.get("/industry/{industry}", response_model=List[AIPersonaResponse], status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_ai_personas_by_industry(
    industry: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get all AI Personas by industry
    """
    personas = await ai_persona_service.get_ai_personas_by_industry(industry, session)
    return personas

@ai_persona_router.put("/{persona_id}", response_model=AIPersonaResponse, status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def update_ai_persona(
    persona_id: str,
    persona_data: AIPersonaUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an AI Persona
    """

    persona = await ai_persona_service.get_ai_persona_by_id(persona_id, session)
    if not persona:
        raise HTTPException(status_code=404, detail="AI Persona not found")
        
    updated_persona = await ai_persona_service.update_ai_persona(persona_id, persona_data, session)
    if not updated_persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Persona not found"
        )
    return updated_persona

@ai_persona_router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_ai_persona(
    persona_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an AI Persona
    """
    success = await ai_persona_service.delete_ai_persona(persona_id, session)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Persona not found"
        )
    return None

@ai_persona_router.post("/generate-all-combinations", status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def generate_all_ai_persona_combinations(
    session: AsyncSession = Depends(get_session)
):
    """
    Generate and add all possible AI Persona combinations to the database.
    Only accessible by admin/super_admin.
    """
    await ai_persona_service.add_all_combinations(session)
    return {"message": "All AI Persona combinations have been added."}

@ai_persona_router.post("/{persona_id}/upload-profile-pic", status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def upload_profile_pic(
    persona_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    try:
    

        # Upload file to Appwrite using utility function
        result = await add_file(file)  # Pass the UploadFile object directly
        file_id = result["$id"]
        logger.info(f"File uploaded successfully with ID: {file_id}")

        # Generate public file URL
        file_url = await get_file_url(file_id)
        logger.info(f"Generated file URL: {file_url}")

        # Update persona's profile picture in DB
        persona = await ai_persona_service.update_ai_persona(
            persona_id,
            AIPersonaUpdate(profile_pic=file_url),
            session
        )

        if not persona:
            raise HTTPException(status_code=404, detail="AI Persona not found")

        return {
            "message": "Profile picture uploaded successfully",
            "profile_pic": file_url
        }

    except Exception as e:
        logger.error(f"Failed to upload profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@ai_persona_router.get("/{persona_id}/profile-pic", response_class=FileResponse, status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_persona_profile_pic(
    persona_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Return the profile picture file for the given AI Persona.
    """
    persona = await ai_persona_service.get_ai_persona_by_id(persona_id, session)
    if not persona or not persona.profile_pic:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    abs_path = os.path.join(os.getcwd(), persona.profile_pic)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Profile picture file missing on server")
    return FileResponse(abs_path, media_type="image/png")