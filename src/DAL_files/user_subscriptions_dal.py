from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.user_subscriptions import UserSubscription
from schemas.user_subscriptions_schemas import UserSubscriptionCreate, UserSubscriptionUpdate
from fastapi import HTTPException

from .subscriptions_dal import SubscriptionDAL
from datetime import datetime, timedelta, timezone

subscription_service = SubscriptionDAL()



class UserSubscriptionDAL:
    async def get_user_subscription_by_id(self, user_subscription_id: str, db_session: AsyncSession) -> UserSubscription:
        result = await db_session.execute(select(UserSubscription).where(UserSubscription.user_subscription_id == user_subscription_id))
        return result.scalar_one_or_none()

    async def get_user_subscriptions_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[UserSubscription]:
        result = await db_session.execute(select(UserSubscription).where(UserSubscription.user_id == user_id))
        return result.scalars().all()

    async def get_user_subscriptions_by_subscription_id(self, subscription_id: str, db_session: AsyncSession) -> list[UserSubscription]:
        result = await db_session.execute(select(UserSubscription).where(UserSubscription.subscription_id == subscription_id))
        return result.scalars().all()

    async def create_user_subscription(self, user_subscription_data: UserSubscriptionCreate, db_session: AsyncSession) -> UserSubscription:
        from DAL_files.users_dal import UserDAL
        user_service = UserDAL()
        # Validate user_id
        user = await user_service.get_user_by_id(str(user_subscription_data.user_id), db_session)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        
        
        # Validate subscription_id
        subscription = await subscription_service.get_subscription_by_id(str(user_subscription_data.subscription_id), db_session)
        if not subscription:
            raise HTTPException(status_code=404, detail='Subscription not found')
        # Check for existing active subscription for this user and subscription_id
        now = datetime.now(timezone.utc)
        result = await db_session.execute(
            select(UserSubscription).where(
                UserSubscription.user_id == str(user_subscription_data.user_id),
                UserSubscription.subscription_id == str(user_subscription_data.subscription_id),
                UserSubscription.end_date > now
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail='Your subscription is not expired yet.')
        # Set start_date and end_date based on billing_cycle
        start_date = now
        if subscription.billing_cycle == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif subscription.billing_cycle == 'yearly':
            end_date = start_date + timedelta(days=365)
        else:
            end_date = start_date
        data = user_subscription_data.model_dump()
        new_user_subscription = UserSubscription(**data)
        new_user_subscription.start_date = start_date
        new_user_subscription.end_date = end_date
        db_session.add(new_user_subscription)
        await db_session.commit()
        await db_session.refresh(new_user_subscription)
        return new_user_subscription

    async def update_user_subscription(self, user_subscription_id: str, update_data: UserSubscriptionUpdate, db_session: AsyncSession) -> UserSubscription:
        user_subscription = await self.get_user_subscription_by_id(user_subscription_id, db_session)
        if not user_subscription:
            return None
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user_subscription, key, value)
        await db_session.commit()
        await db_session.refresh(user_subscription)
        return user_subscription

    async def delete_user_subscription(self, user_subscription_id: str, db_session: AsyncSession) -> bool:
        user_subscription = await self.get_user_subscription_by_id(user_subscription_id, db_session)
        if not user_subscription:
            return False
        await db_session.delete(user_subscription)
        await db_session.commit()
        return True 