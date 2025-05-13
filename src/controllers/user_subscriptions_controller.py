from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.user_subscriptions_schemas import UserSubscriptionCreate, UserSubscriptionUpdate, UserSubscriptionResponse
from database import get_session
from DAL_files.user_subscriptions_dal import UserSubscriptionDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

user_subscriptions_router = APIRouter()
user_subscription_service = UserSubscriptionDAL()

@user_subscriptions_router.post("/", response_model=UserSubscriptionResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_user_subscription(
    user_subscription_data: UserSubscriptionCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new user subscription
    """
    created = await user_subscription_service.create_user_subscription(user_subscription_data, session)
    return created

@user_subscriptions_router.get("/{user_subscription_id}", response_model=UserSubscriptionResponse, status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_user_subscription_by_id(
    user_subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get a user subscription by ID
    """
    user_subscription = await user_subscription_service.get_user_subscription_by_id(user_subscription_id, session)
    if not user_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")
    return user_subscription

@user_subscriptions_router.get("/by-user/{user_id}", response_model=list[UserSubscriptionResponse], status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_user_subscriptions_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get user subscriptions by user ID
    """
    user_subscriptions = await user_subscription_service.get_user_subscriptions_by_user_id(user_id, session)
    return user_subscriptions

@user_subscriptions_router.get("/by-subscription/{subscription_id}", response_model=list[UserSubscriptionResponse], status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_user_subscriptions_by_subscription_id(
    subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get user subscriptions by subscription ID
    """
    user_subscriptions = await user_subscription_service.get_user_subscriptions_by_subscription_id(subscription_id, session)
    return user_subscriptions

@user_subscriptions_router.put("/{user_subscription_id}", response_model=UserSubscriptionResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def update_user_subscription(
    user_subscription_id: str,
    update_data: UserSubscriptionUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update a user subscription
    """
    updated = await user_subscription_service.update_user_subscription(user_subscription_id, update_data, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")
    return updated

@user_subscriptions_router.delete("/{user_subscription_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_user_subscription(
    user_subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a user subscription
    """
    success = await user_subscription_service.delete_user_subscription(user_subscription_id, session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User subscription not found")
    return None 