from sqlalchemy.orm import Session
from uuid import UUID
from models.feedback import Feedback
from schemas.feedback_schemas import FeedbackCreate, FeedbackUpdate

class FeedbackDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_feedback(self, feedback_data: FeedbackCreate) -> Feedback:
        new_feedback = Feedback(
            user_id=feedback_data.user_id,
            session_id=feedback_data.session_id,
            rating=feedback_data.rating,
            comment=feedback_data.comment,
        )
        self.db_session.add(new_feedback)
        await self.db_session.flush()
        return new_feedback

    async def get_feedback_by_id(self, feedback_id: str) -> Feedback:
        return await self.db_session.get(Feedback, feedback_id)

    async def get_feedback_by_user_id(self, user_id: str) -> list[Feedback]:
        result = await self.db_session.execute(
            self.db_session.query(Feedback).filter(Feedback.user_id == user_id)
        )
        return result.scalars().all()

    async def get_feedback_by_session_id(self, session_id: str) -> list[Feedback]:
        result = await self.db_session.execute(
            self.db_session.query(Feedback).filter(Feedback.session_id == session_id)
        )
        return result.scalars().all()

    async def update_feedback(self, feedback_id: str, feedback_data: FeedbackUpdate) -> Feedback:
        feedback = await self.get_feedback_by_id(feedback_id)
        if not feedback:
            return None
        for key, value in feedback_data.dict(exclude_unset=True).items():
            setattr(feedback, key, value)
        await self.db_session.flush()
        return feedback

    async def delete_feedback(self, feedback_id: str) -> bool:
        feedback = await self.get_feedback_by_id(feedback_id)
        if not feedback:
            return False
        await self.db_session.delete(feedback)
        await self.db_session.flush()
        return True