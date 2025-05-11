from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from uuid import UUID

from database import get_session
from DAL_files.interaction_modes_dal import InteractionModeDAL
from schemas.interaction_modes_schemas import InteractionModeCreate, InteractionModeUpdate, InteractionModeResponse
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

# Create different role checkers for different access levels
admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

interaction_modes_router = APIRouter()
interaction_mode_service = InteractionModeDAL()

@interaction_modes_router.post("/", response_model=InteractionModeResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_interaction_mode(
    mode_data: InteractionModeCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new interaction mode (Admin only)
    """
    try:
        # Check if mode with same name exists
        existing_mode = await interaction_mode_service.get_mode_by_name(mode_data.name, session)
        if existing_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An interaction mode with this name already exists"
            )
        
        new_mode = await interaction_mode_service.create_mode(mode_data, session)
        return new_mode
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@interaction_modes_router.get("/", response_model=List[InteractionModeResponse], status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_all_modes(
    session: AsyncSession = Depends(get_session)
):
    """
    Get all interaction modes (Manager and above)
    """
    modes = await interaction_mode_service.get_all_modes(session)
    return modes

@interaction_modes_router.get("/{mode_id}", response_model=InteractionModeResponse, status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_mode_by_id(
    mode_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get interaction mode by ID (Sales and above)
    """
    mode = await interaction_mode_service.get_mode_by_id(mode_id, session)
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction mode not found"
        )
    return mode

@interaction_modes_router.get("/by-name/{name}", response_model=InteractionModeResponse, status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_mode_by_name(
    name: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get interaction mode by name (Sales and above)
    """
    mode = await interaction_mode_service.get_mode_by_name(name, session)
    if not mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction mode not found"
        )
    return mode

@interaction_modes_router.put("/{mode_id}", response_model=InteractionModeResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def update_mode(
    mode_id: str,
    mode_data: InteractionModeUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an interaction mode (Admin only)
    """
    try:
        updated_mode = await interaction_mode_service.update_mode(mode_id, mode_data, session)
        if not updated_mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction mode not found"
            )
        return updated_mode
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@interaction_modes_router.delete("/{mode_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_mode(
    mode_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an interaction mode (Admin only)
    """
    try:
        success = await interaction_mode_service.delete_mode(mode_id, session)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction mode not found"
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return 