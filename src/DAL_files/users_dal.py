from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.users import User
from schemas.users_schemas import UserCreate, UserUpdate
from utils import generate_passwd_hash
from sqlalchemy.exc import IntegrityError
from .roles_dal import RoleDAL
from .subscriptions_dal import SubscriptionDAL
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from config import settings
import logging
from fastapi import HTTPException

roles_services = RoleDAL()
subscriptions_services = SubscriptionDAL()
logger = logging.getLogger(__name__)

class UserDAL:

  
    async def create_user(self, user_data: UserCreate, db_session: AsyncSession) -> User:
        # Convert the Pydantic model to a dictionary
        user_data_dict = user_data.model_dump()

        # Extract and remove the 'password' and 'google_id' fields from the dictionary
        raw_password = user_data_dict.pop("password", None)
        google_id = user_data_dict.get("google_id")

        # Validate that either a password or google_id is provided, but not both
        if google_id and raw_password:
            raise HTTPException(status_code=400, detail="A user cannot have both a password and a google_id.")
        if not google_id and not raw_password:
            raise HTTPException(status_code=400, detail="Either a password or a google_id is required to create a user.")

        # Hash the password if google_id is not provided
        password_hash = generate_passwd_hash(raw_password) if not google_id else None

        # Create the User instance without the 'password' field
        new_user = User(**user_data_dict)

        # Assign the hashed password to the 'password_hash' field
        new_user.password_hash = password_hash

        # Assign the default role to the user
        default_role = await roles_services.get_role_by_name("sales_person", db_session)
        if not default_role:
            raise HTTPException(status_code=500, detail="Default role not found")
        
        default_subscription = await subscriptions_services.get_subscription_by_plan_type("free_trial", db_session)
        if not default_subscription:
            raise HTTPException(status_code=500, detail="Default subscription not found")

        new_user.subscription_id = default_subscription.subscription_id
        new_user.role_id = default_role.role_id

        # Add the new user to the session and commit
        try:
            db_session.add(new_user)
            await db_session.commit()
            await db_session.refresh(new_user)
        except IntegrityError as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create user: {e}")

        return new_user

    async def get_user_by_id(self, user_id: str,db_session: AsyncSession) -> User:
        return await db_session.get(User, user_id)

    async def get_user_by_email(self, email: str,db_session: AsyncSession) -> User:
        result = await db_session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: str, user_data: UserUpdate, db_session: AsyncSession) -> User:
        user = await self.get_user_by_id(user_id, db_session)
        if not user:
            return None
        for key, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def delete_user(self, user_id: str,db_session: AsyncSession) -> bool:
        user = await self.get_user_by_id(user_id, db_session)
        if not user:
            return False
        await db_session.delete(user)
        await db_session.commit()

        return True
    
    async def change_user_role(self, user_id: str, new_role_id: str, db_session: AsyncSession) -> User:

        # Fetch the user by ID
        user = await self.get_user_by_id(user_id, db_session)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")

        # Verify that the new role exists
        new_role = await roles_services.get_role_by_id(new_role_id, db_session)
        if not new_role:
            raise HTTPException(status_code=404, detail=f"Role with ID {new_role_id} not found.")

        # Update the user's role
        user.role_id = new_role_id

        try:
            # Commit the changes to the database
            await db_session.commit()
            await db_session.refresh(user)
        except IntegrityError as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to change user role: {e}")

        return user
    
    async def get_all_users(self, db_session: AsyncSession) -> list[User]:

            # Query all users from the database
            result = await db_session.execute(select(User))
            users = result.scalars().all()
            return users
    
    async def verify_google_token(self,id_token: str):
        """
        Verifies the Google ID token and extracts user information.
        """
        try:
            print("token_id", id_token)
            # Verify the Google ID token using the Google API client library
            idinfo = google_id_token.verify_oauth2_token(
                id_token, google_requests.Request(), settings.google_client_id
            )
            print("Verified token info:", idinfo)

            # Ensure the token is issued by Google and intended for your app
            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise HTTPException(status_code=400, detail="Invalid token issuer.")

            # Extract relevant user information
            user_info = {
                "sub": idinfo["sub"],  # Google unique user ID
                "email": idinfo.get("email"),
                "first_name": idinfo.get("given_name", ""),
                "last_name": idinfo.get("family_name", ""),
                "picture": idinfo.get("picture", ""),  # Optional: profile picture URL
            }

            return user_info

        except ValueError as e:
            # Token is invalid
            return None




















