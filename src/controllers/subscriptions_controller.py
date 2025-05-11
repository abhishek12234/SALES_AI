from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.subscriptions_schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from database import get_session
from DAL_files.subscriptions_dal import SubscriptionDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum
from datetime import datetime


# Create different role checkers for different access levels
admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

subscriptions_router = APIRouter()

subscription_service = SubscriptionDAL()

@subscriptions_router.post("/purchase/{subscription_id}", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new subscription
    """
    user_id = current_user.user_id
    # Check for active subscriptions (where end_date is in the future)
    try:
        created_subscription = await subscription_service.purchase_subscription(user_id ,subscription_id, session)
        return created_subscription
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@subscriptions_router.post("/",response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new subscription
    """
    
    created_subscription = await subscription_service.create_subscription(subscription_data, session)
    return created_subscription


@subscriptions_router.get("/{subscription_id}", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_subscription_by_id(
    subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get a subscription by ID
    """
    subscription = await subscription_service.get_subscription_by_id(subscription_id, session)
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return subscription

@subscriptions_router.get("/", response_model=list[SubscriptionResponse], status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_all_subscriptions(
    session: AsyncSession = Depends(get_session)
):
    """
    Get all subscriptions
    """
    subscriptions = await subscription_service.get_all_subscriptions(session)
    return subscriptions

@subscriptions_router.get("/by-user/{user_id}", response_model=list[SubscriptionResponse], status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_subscriptions_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get subscriptions by user ID
    """
    subscriptions = await subscription_service.get_subscriptions_by_user_id(user_id, session)
    return subscriptions

@subscriptions_router.put("/{subscription_id}", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def update_subscription(
    subscription_id: str,
    subscription_update: SubscriptionUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Update a subscription
    """
    updated_subscription = await subscription_service.update_subscription(subscription_id, subscription_update, session)
    if not updated_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return updated_subscription

@subscriptions_router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_subscription(
    subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Delete a subscription
    """
    success = await subscription_service.delete_subscription(subscription_id, session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return None