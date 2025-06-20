from fastapi import APIRouter, HTTPException, BackgroundTasks
from DAL_files.ai_coaching_dal import AICoachingDAL
from schemas.users_schemas import UserBase
from fastapi import Depends
from dependencies import get_current_user
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from DAL_files.sessions_dal import SessionDAL
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

# Router and service initialization
ai_coaching_router = APIRouter()
ai_coaching_service = AICoachingDAL()
session_services = SessionDAL()

# Pydantic models for request/response
class CoachingFeedbackResponse(BaseModel):
    feedback_id: str
    feedback: str
    timestamp: str
    analysis_id: str
    message_count_at_time: int
    trigger_type: str

class CoachingStatusResponse(BaseModel):
    user_id: str
    session_id: str
    is_monitoring: bool
    message_count: int
    feedback_count: int
    monitoring_started_at: Optional[str] = None
    last_checked: Optional[str] = None

class StartCoachingResponse(BaseModel):
    message: str
    user_id: str
    session_id: str
    initial_message_count: int
    monitoring_status: str

class StopCoachingResponse(BaseModel):
    message: str
    user_id: str
    session_id: str
    monitoring_status: str


@ai_coaching_router.post("/coaching/start/{session_id}", response_model=StartCoachingResponse)
async def start_ai_coaching(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Start AI coaching monitoring for a specific session.

    This endpoint:
    1. Verifies the session exists and belongs to the user
    2. Checks if coaching is already active
    3. Starts background monitoring for new messages
    4. Returns the initial status
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        if user_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found or does not belong to you."
            )

        user_id = current_user.user_id

        # Check if already monitoring
        if ai_coaching_service.is_monitoring_active(user_id, session_id):
            raise HTTPException(
                status_code=400,
                detail="AI coaching is already active for this session."
            )

        # Verify session has conversation data
        session_data = await ai_coaching_service.get_session_data(user_id, session_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="No conversation data found in Redis for this session."
            )

        messages = session_data.get("messages", [])
        if len(messages) < 1:
            raise HTTPException(
                status_code=400,
                detail="Session needs at least 1 message to start coaching."
            )

        # Start monitoring
        success = await ai_coaching_service.start_monitoring_session(user_id, session_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to start AI coaching monitoring."
            )

        return StartCoachingResponse(
            message="AI coaching started successfully and monitoring for new messages",
            user_id=user_id,
            session_id=session_id,
            initial_message_count=len(messages),
            monitoring_status="active"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error starting AI coaching: {str(e)}"
        )


@ai_coaching_router.get("/coaching/feedback/{session_id}")
async def get_coaching_feedback(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all AI coaching feedback for a session.

    This endpoint returns all coaching feedback that has been generated
    for the specified session, whether from monitoring or manual analysis.
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        if user_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found or does not belong to you."
            )

        user_id = current_user.user_id

        # Get coaching feedback history
        feedback_history = await ai_coaching_service.get_coaching_feedback(user_id, session_id)

        # Format response
        formatted_feedback = []
        for feedback in feedback_history:
            formatted_feedback.append(CoachingFeedbackResponse(
                feedback_id=feedback.get("analysis_id", "unknown"),
                feedback=feedback.get("feedback", ""),
                timestamp=feedback.get("timestamp", ""),
                analysis_id=feedback.get("analysis_id", ""),
                message_count_at_time=feedback.get("message_count_at_time", 0),
                trigger_type=feedback.get("trigger_type", "unknown")
            ))

        return {
            "user_id": user_id,
            "session_id": session_id,
            "feedback_history": formatted_feedback,
            "total_feedback_count": len(formatted_feedback),
            "is_monitoring_active": ai_coaching_service.is_monitoring_active(user_id, session_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving coaching feedback: {str(e)}"
        )


@ai_coaching_router.get("/coaching/status/{session_id}", response_model=CoachingStatusResponse)
async def get_coaching_status(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get the current AI coaching status for a session.

    This endpoint returns:
    - Whether monitoring is active
    - Current message count
    - Number of coaching feedback entries
    - Monitoring start time and last check time
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        if user_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found or does not belong to you."
            )

        user_id = current_user.user_id

        # Check monitoring status
        is_monitoring = ai_coaching_service.is_monitoring_active(user_id, session_id)
        monitoring_info = ai_coaching_service.get_monitoring_status(user_id, session_id)

        # Get current session data
        session_data = await ai_coaching_service.get_session_data(user_id, session_id)
        message_count = len(session_data.get("messages", [])) if session_data else 0

        # Get coaching feedback count
        feedback_history = await ai_coaching_service.get_coaching_feedback(user_id, session_id)
        feedback_count = len(feedback_history)

        return CoachingStatusResponse(
            user_id=user_id,
            session_id=session_id,
            is_monitoring=is_monitoring,
            message_count=message_count,
            feedback_count=feedback_count,
            monitoring_started_at=monitoring_info.get("started_at") if monitoring_info else None,
            last_checked=monitoring_info.get("last_checked") if monitoring_info else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting coaching status: {str(e)}"
        )


@ai_coaching_router.post("/coaching/stop/{session_id}", response_model=StopCoachingResponse)
async def stop_ai_coaching(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Stop AI coaching monitoring for a specific session.

    This endpoint:
    1. Verifies the session exists and belongs to the user
    2. Stops the background monitoring task
    3. Cleans up monitoring resources
    4. Returns the final status
    """
    try:
        # Verify session exists and belongs to user
        user_session = await session_services.get_session_by_id_and_user_id(
            session_id, current_user.user_id, session
        )
        if user_session is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found or does not belong to you."
            )

        user_id = current_user.user_id

        # Check if monitoring is active
        if not ai_coaching_service.is_monitoring_active(user_id, session_id):
            raise HTTPException(
                status_code=400,
                detail="No active AI coaching monitoring found for this session."
            )

        # Stop monitoring
        success = ai_coaching_service.stop_monitoring_session(user_id, session_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to stop AI coaching monitoring."
            )

        return StopCoachingResponse(
            message="AI coaching monitoring stopped successfully",
            user_id=user_id,
            session_id=session_id,
            monitoring_status="stopped"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error stopping AI coaching: {str(e)}"
        )


# Additional utility endpoint for debugging/admin
@ai_coaching_router.get("/coaching/admin/active-sessions")
async def get_all_active_coaching_sessions(
    current_user: UserBase = Depends(get_current_user)
):
    """
    Get all active coaching sessions (for debugging/admin purposes).
    """
    try:
        active_sessions = ai_coaching_service.get_all_active_monitoring()
        return {
            "active_sessions_count": len(active_sessions),
            "active_sessions": active_sessions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting active sessions: {str(e)}"
        )