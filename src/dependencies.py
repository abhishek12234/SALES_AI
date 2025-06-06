from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from utils import decode_token
from fastapi.exceptions import HTTPException
from database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from DAL_files.users_dal import UserDAL
from DAL_files.roles_dal import RoleDAL
from typing import List, Any
from schemas.users_schemas import UserBase
from redis_store import token_in_blocklist

user_service=UserDAL()
role_service=RoleDAL()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)    

        token= creds.credentials
        token_data=decode_token(token)

        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="invalid or expired token" 
            )
    
        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="token has been blacklisted"
            )
        
        self.verify_token_data(token_data)
       
        return token_data
    
    def token_valid(self,token:str)->bool:
        token_data=decode_token(token)
        return token_data is not None 
    
    def verify_token_data(self,token_data):
         raise NotImplementedError("please Override this method in chile class")
    
class AccessTokenBearer(TokenBearer):
     def verify_token_data(self,token_data:dict)->None:
          
            if token_data and token_data["refresh"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="provide an access token"
                    )
class RefreshTokenBearer(TokenBearer):
     def verify_token_data(self,token_data:dict)->None:
          
            if token_data and not token_data["refresh"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="provide a Refresh token"
                    )

async def get_current_user(
    token_detail: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
):
    user_email = token_detail.get("user", {}).get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token payload: missing 'user.email'."
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: UserBase = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> bool:
        role = await role_service.get_role_by_id(current_user.role_id, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not found."
            )

        if role.name in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required role to access this resource."
        )