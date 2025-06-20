from fastapi import APIRouter, HTTPException, Depends
from DAL_files.ai_coaching_dal import AICoachingDAL
from DAL_files.sessions_dal import SessionDAL
from schemas.users_schemas import UserBase
from dependencies import get_current_user
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# Create router
ai_coaching_router = APIRouter(tags=["AI Coaching"])

# Initialize services
ai_coaching_service = AICoachingDAL()
session_services = SessionDAL()

@ai_coaching_router.get("/feedback/{session_id}")
async def get_coaching_feedback(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get comprehensive AI coaching feedback for a specific chat session.
    
    - **session_id**: The ID of the chat session to analyze
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        
        if user_session is None:
            raise HTTPException(
                status_code=404, 
                detail="Session not found or you don't have access to this session."
            )

        # Get coaching feedback
        coaching_result = await ai_coaching_service.generate_coaching_feedback(
            user_id=current_user.user_id,
            session_id=session_id
        )

        if coaching_result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=coaching_result["message"]
            )
        
        if coaching_result["status"] == "no_data":
            return {
                "success": False,
                "message": "No conversation data available for coaching analysis.",
                "session_id": session_id
            }

        if coaching_result["status"] == "insufficient_data":
            return {
                "success": False,
                "message": coaching_result["message"],
                "session_id": session_id
            }

        return {
            "success": True,
            "session_id": session_id,
            "session_info": coaching_result["session_info"],
            "coaching_feedback": coaching_result["coaching_feedback"],
            "conversation_summary": coaching_result["conversation_summary"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@ai_coaching_router.get("/messages/{session_id}")
async def get_session_messages(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all messages from a chat session for review.
    
    - **session_id**: The ID of the chat session to retrieve messages from
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        
        if user_session is None:
            raise HTTPException(
                status_code=404, 
                detail="Session not found or you don't have access to this session."
            )

        # Get messages
        messages = await ai_coaching_service.get_session_messages(
            user_id=current_user.user_id,
            session_id=session_id
        )

        return {
            "success": True,
            "session_id": session_id,
            "message_count": len(messages),
            "messages": messages
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@ai_coaching_router.get("/health")
async def health_check():
    """Health check endpoint for the AI coaching service."""
    return {
        "status": "healthy",
        "service": "AI Coaching System",
        "version": "1.0.0"
    }