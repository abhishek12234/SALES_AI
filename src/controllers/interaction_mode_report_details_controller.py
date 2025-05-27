from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.interaction_mode_report_details_schemas import InteractionModeReportDetailBase, InteractionModeReportDetailResponse
from database import get_session
from DAL_files.interaction_mode_report_details_dal import InteractionModeReportDetailDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum
from DAL_files.interaction_modes_dal import InteractionModeDAL
import logging

logger = logging.getLogger("interaction_mode_report_details")
super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

interaction_mode_report_details_router = APIRouter()
service = InteractionModeReportDetailDAL()
intraction_mode_service = InteractionModeDAL()

@interaction_mode_report_details_router.post("/", response_model=InteractionModeReportDetailResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create(model: InteractionModeReportDetailBase, session: AsyncSession = Depends(get_session)):
    
    if not await intraction_mode_service.mode_exists(model.mode_id, session):
        raise HTTPException(status_code=400, detail="Invalid mode_id: Interaction mode does not exist.")
    try:
        created = await service.create(model, session)
        return created
    except Exception as e:
        logger.exception("Failed to create interaction mode report detail")
        raise HTTPException(status_code=500, detail=str(e))

@interaction_mode_report_details_router.get("/{id}", response_model=InteractionModeReportDetailResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_by_id(id: str, session: AsyncSession = Depends(get_session)):
    obj = await service.get_by_id(id, session)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return obj

@interaction_mode_report_details_router.get("/", response_model=list[InteractionModeReportDetailResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all(session: AsyncSession = Depends(get_session)):
    return await service.get_all(session)

@interaction_mode_report_details_router.put("/{id}", response_model=InteractionModeReportDetailResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update(id: str, model: InteractionModeReportDetailBase, session: AsyncSession = Depends(get_session)):
    updated = await service.update(id, model, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return updated

@interaction_mode_report_details_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete(id: str, session: AsyncSession = Depends(get_session)):
    deleted = await service.delete(id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return 