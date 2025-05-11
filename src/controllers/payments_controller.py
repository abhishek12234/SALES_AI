from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.payments_schemas import PaymentCreate, PaymentUpdate, PaymentResponse
from database import get_session
from DAL_files.payments_dal import PaymentDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

payments_router = APIRouter()
payment_service = PaymentDAL()

@payments_router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_payment(
    payment_data: PaymentCreate,
    session: AsyncSession = Depends(get_session)
):
    created_payment = await payment_service.create_payment(payment_data, session)
    return created_payment

@payments_router.get("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_payment_by_id(
    payment_id: str,
    session: AsyncSession = Depends(get_session)
):
    payment = await payment_service.get_payment_by_id(payment_id, session)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment

@payments_router.get("/", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_all_payments(
    session: AsyncSession = Depends(get_session)
):
    payments = await payment_service.get_all_payments(session)
    return payments

@payments_router.get("/by-user/{user_id}", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK, dependencies=[sales_checker])
async def get_payments_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    payments = await payment_service.get_payments_by_user_id(user_id, session)
    return payments

@payments_router.get("/by-subscription/{subscription_id}", response_model=list[PaymentResponse], status_code=status.HTTP_200_OK, dependencies=[manager_checker])
async def get_payments_by_subscription_id(
    subscription_id: str,
    session: AsyncSession = Depends(get_session)
):
    payments = await payment_service.get_payments_by_subscription_id(subscription_id, session)
    return payments

@payments_router.put("/{payment_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate,
    session: AsyncSession = Depends(get_session)
):
    updated_payment = await payment_service.update_payment(payment_id, payment_update, session)
    if not updated_payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return updated_payment

@payments_router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_payment(
    payment_id: str,
    session: AsyncSession = Depends(get_session)
):
    success = await payment_service.delete_payment(payment_id, session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return None

@payments_router.post("/purchase", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def purchase_subscription(
    plan_type: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Purchase a subscription for the authenticated user (with payment validation).
    """
    user_id = current_user.user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user context.")
    try:
        payment = await payment_service.purchase_subscription(user_id, plan_type, session)
        return payment
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Payment creation logic not implemented.")
    except HTTPException as e:
        raise e 