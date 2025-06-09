from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.sessions_schemas import SessionCreate, SessionUpdate, SessionResponse, PersonaData
from database import get_session
from DAL_files.sessions_dal import SessionDAL
from schemas.users_schemas import UserBase
from dependencies import get_current_user
from DAL_files.ai_persona_dal import AIPersonaDAL
from DAL_files.manufacturing_models_dal import ManufacturingModelDAL
from DAL_files.interaction_modes_dal import InteractionModeDAL
from DAL_files.industries_dal import IndustryDAL
from DAL_files.ai_roles_dal import AIRoleDAL
from DAL_files.plant_size_impacts_dal import PlantSizeImpactDAL
from redis_store import store_prompt_template

sessions_router = APIRouter()
session_service = SessionDAL()
persona_service = AIPersonaDAL()
manufacturing_model_service = ManufacturingModelDAL()
intraction_mode_service = InteractionModeDAL()
industry_service = IndustryDAL()
ai_role_service = AIRoleDAL()
plant_size_impact_service = PlantSizeImpactDAL()

@sessions_router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    
    try:
        persona_data = await persona_service.get_ai_persona_by_id(session_data.persona_id,session)
        if not persona_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
            
        print("person_data", persona_data.ai_role_id=="ad42431d-46eb-4905-8c2c-16b897453905", "persona_data")

        intraction_mode = await intraction_mode_service.get_mode_by_id(session_data.mode_id,session)
        if not intraction_mode:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mode not found")
        

        manufacturing_model = await manufacturing_model_service.get_manufacturing_model_by_id(persona_data.manufacturing_model_id,session)
        if not manufacturing_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturing model not found")
        
        industry = await industry_service.get_industry_by_id(persona_data.industry_id,session)
        if not industry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry not found")
        
        ai_role = await ai_role_service.get_ai_role_by_id(persona_data.ai_role_id,session)
        if not ai_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI role not found")
        
        plant_size_impact = await plant_size_impact_service.get_plant_size_impact_by_id(persona_data.plant_size_impact_id,session)
        if not plant_size_impact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant size impact not found")
            
        geography = persona_data.geography
        #exprience_level = persona_data.experience_level

        prompt_template = intraction_mode.prompt_template
        prompt_template = prompt_template.format(
            industry=industry.name,
            behavioral_detail=persona_data.behavioral_detail,
            industry_details=industry.details,
            #experience_level=exprience_level,
            role=ai_role.name,
            role_details=ai_role.description,
            name=persona_data.name,
            plant_size_impact=plant_size_impact.name,
            plant_size_impact_details=plant_size_impact.description,
            manufacturing_model=manufacturing_model.name,
            manufacturing_model_details=manufacturing_model.description,
            geography=geography
        )

        user_id=current_user.user_id
        created_session = await session_service.create_session(user_id,session_data.persona_id,session_data.mode_id,session)
        if not created_session:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session creation failed")

        try:
          await store_prompt_template(user_id, created_session.session_id, prompt_template)
        except Exception as e:
            await session_service.delete_session(created_session.session_id,session)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store prompt template")
        
        return created_session
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@sessions_router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def get_session_by_id(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_id=current_user.user_id
    session_data = await session_service.get_session_by_id_and_user_id(session_id,user_id,session)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your Session not found")
    return session_data

@sessions_router.get("/by-user/{user_id}", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    
    sessions = await session_service.get_sessions_by_user_id(user_id,session)
    return sessions


@sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    
    success = await session_service.delete_session(session_id,session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return