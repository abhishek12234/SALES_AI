from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.payments import Payment
from models.subscriptions import Subscription
from schemas.payments_schemas import PaymentCreate, PaymentUpdate
from fastapi import HTTPException
from datetime import datetime

class PaymentDAL:
    async def create_payment(self, payment_data: PaymentCreate, db_session: AsyncSession) -> Payment:
        new_payment = Payment(**payment_data.model_dump())
        db_session.add(new_payment)
        await db_session.commit()
        await db_session.refresh(new_payment)
        return new_payment

    async def get_payment_by_id(self, payment_id: str, db_session: AsyncSession) -> Payment:
        return await db_session.get(Payment, payment_id)

    async def get_all_payments(self, db_session: AsyncSession) -> list[Payment]:
        result = await db_session.execute(select(Payment))
        return result.scalars().all()

    async def get_payments_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[Payment]:
        result = await db_session.execute(select(Payment).where(Payment.user_id == user_id))
        return result.scalars().all()

    async def get_payments_by_subscription_id(self, subscription_id: str, db_session: AsyncSession) -> list[Payment]:
        result = await db_session.execute(select(Payment).where(Payment.subscription_id == subscription_id))
        return result.scalars().all()

    async def update_payment(self, payment_id: str, payment_data: PaymentUpdate, db_session: AsyncSession) -> Payment:
        payment = await self.get_payment_by_id(payment_id, db_session)
        if not payment:
            return None
        for key, value in payment_data.model_dump(exclude_unset=True).items():
            setattr(payment, key, value)
        await db_session.commit()
        await db_session.refresh(payment)
        return payment

    async def delete_payment(self, payment_id: str, db_session: AsyncSession) -> bool:
        payment = await self.get_payment_by_id(payment_id, db_session)
        if not payment:
            return False
        await db_session.delete(payment)
        await db_session.commit()
        return True

    async def purchase_subscription(self, user_id: str, plan_type: str, db_session: AsyncSession) -> Payment:
        # Get all subscriptions for the user
        result = await db_session.execute(select(Subscription).where(Subscription.user_id == user_id))
        existing_subscriptions = result.scalars().all()
        # Check for active subscriptions of the same plan type
        active_subscriptions = [
            sub for sub in existing_subscriptions
            if sub.end_date > datetime.now().date() and sub.plan_type == plan_type and sub.status_active
        ]
        if active_subscriptions:
            raise HTTPException(status_code=400, detail=f"User already has an active {plan_type} subscription.")
        # Here you would create a Payment record (and possibly a new Subscription if needed)
        # This is a placeholder for actual payment creation logic
        # payment_data = PaymentCreate(...)
        # return await self.create_payment(payment_data, db_session)
        raise NotImplementedError("Implement payment creation logic here.") 