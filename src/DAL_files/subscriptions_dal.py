from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.subscriptions import Subscription
from schemas.subscriptions_schemas import SubscriptionCreate, SubscriptionUpdate
from sqlalchemy.sql import exists
from fastapi import HTTPException

class SubscriptionDAL:
    async def subscription_exists(self, subscription_id: str, db_session: AsyncSession) -> bool:
        result = await db_session.execute(select(Subscription).where(Subscription.subscription_id == subscription_id))
        print(f"Subscription exists: {subscription_id}", '--------------------------------')
        return result.scalar_one_or_none() is not None

    async def get_all_subscriptions(self, db_session: AsyncSession) -> list[Subscription]:
        result = await db_session.execute(select(Subscription))
        return result.scalars().all()

    async def get_subscription_by_id(self, subscription_id: str, db_session: AsyncSession) -> Subscription:
        # Check if the subscription exists
        subscription = await self.subscription_exists(subscription_id, db_session)
        if not subscription:
            return None
        return await db_session.get(Subscription, subscription_id)

    async def get_subscriptions_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[Subscription]:
        result = await db_session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalars().all()

    async def update_subscription(self, subscription_id: str, subscription_data: SubscriptionUpdate, db_session: AsyncSession) -> Subscription:
        subscription = await self.get_subscription_by_id(subscription_id, db_session)
        if not subscription:
            return None
        for key, value in subscription_data.model_dump(exclude_unset=True).items():
            setattr(subscription, key, value)
        await db_session.commit()
        await db_session.refresh(subscription)
        return subscription

    async def delete_subscription(self, subscription_id: str, db_session: AsyncSession) -> bool:
        subscription = await self.get_subscription_by_id(subscription_id, db_session)
        if not subscription:
            return False
        await db_session.delete(subscription)
        await db_session.commit()
        return True

    async def get_subscription_by_plan_type(self, plan_type: str, db_session: AsyncSession) -> Subscription:
        result = await db_session.execute(
            select(Subscription).where(Subscription.plan_type == plan_type)
        )
        return result.scalars().first()

    async def create_subscription(self, subscription_data: SubscriptionCreate, db_session: AsyncSession) -> Subscription:
        new_subscription = Subscription(
            plan_type=subscription_data.plan_type,
            start_date=subscription_data.start_date,
            end_date=subscription_data.end_date,
        )
        db_session.add(new_subscription)
        await db_session.commit()
        await db_session.refresh(new_subscription)
        return new_subscription