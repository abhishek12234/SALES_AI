from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models.performance_reports import PerformanceReport
from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
import json
from datetime import datetime
import os
from sqlalchemy import select
from dotenv import load_dotenv
from config import settings

load_dotenv()

# Pydantic model for structured output
class PerformanceAnalysis(BaseModel):
    overall_score: int = Field(description="Overall performance score (0-100)")
    engagement_level: int = Field(description="Customer engagement level score (0-100)")
    communication_level: int = Field(description="Communication effectiveness score (0-100)")
    objection_handling: int = Field(description="Objection handling skills score (0-100)")
    adaptability: int = Field(description="Adaptability in conversation score (0-100)")
    persuasiveness: int = Field(description="Persuasiveness level score (0-100)")
    create_interest: int = Field(description="Ability to create customer interest score (0-100)")
    sale_closing: int = Field(description="Sale closing effectiveness score (0-100)")
    discovery: int = Field(description="Discovery and needs assessment score (0-100)")
    cross_selling: int = Field(description="Cross-selling opportunities identified score (0-100)")
    solution_fit: int = Field(description="Solution fit assessment score (0-100)")
    coaching_summary: str = Field(description="Detailed coaching summary with specific examples and recommendations")

class PerformanceReportDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

        # Initialize Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Using the same model as chat system
            google_api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCD5cJgxk11YYhM8CeVAvNzmkhpLUaVes8"),
            temperature=0.1
        )

        # Setup output parser
        self.parser = JsonOutputParser(pydantic_object=PerformanceAnalysis)

        # Build the analysis chain
        self._setup_analysis_chain()

    def _setup_analysis_chain(self):
        """Set up LCEL chain for performance analysis."""
        self.analysis_chain = (
            {
                "conversation": RunnablePassthrough(),
                "prompt_template": RunnablePassthrough(),
                "format_instructions": lambda _: self.parser.get_format_instructions()
            }
            | PromptTemplate(
                template="""You are an AI sales performance analyst. Analyze the following sales conversation and provide a comprehensive performance evaluation.

            {prompt_template}

            Conversation to analyze:
            {conversation}

            {format_instructions}

            Provide your analysis as a JSON object with all required fields. Ensure all numeric scores are between 0-100.""",
                            input_variables=["conversation", "prompt_template"],
                            partial_variables={"format_instructions": self.parser.get_format_instructions()}
                        )
                        | self.llm
                        | self.parser
                    )

    async def get_session_history(self, user_id: str, session_id: str) -> list:
        try:
            history = UpstashRedisChatMessageHistory(
                url=settings.upstash_redis_rest_url,
                token=settings.upstash_redis_rest_token,
                session_id=f"user:{user_id}:session:{session_id}"
            )
            messages = history.messages or []
            return [
                {
                    "role": "assistant" if msg.type == "ai" else "human",
                    "content": msg.content
                } for msg in messages
            ]
        except Exception as e:
            print(f"Error retrieving session history: {str(e)}")
            return []

    async def generate_performance_report(self, user_id: str, session_id: str, prompt_template: str) -> PerformanceAnalysis:
        try:
            #chat_history = await self.get_session_history(user_id, session_id)
            chat_history = await self.get_session_history("01234f0f-1612-43d8-95ad-10541f596be9", "b4dcc278-00d7-47fa-a0bd-6a0cb2dba52d")
            if not chat_history:
                raise Exception("No chat history found for this session")

            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in chat_history
            ])

            result = await self.analysis_chain.ainvoke({
                "conversation": conversation_text,
                "prompt_template": prompt_template
            })

            return result  # Parsed PerformanceAnalysis object
        except Exception as e:
            print(f"Error generating performance report: {str(e)}")
            raise Exception(f"Failed to generate performance report: {str(e)}")

    async def get_performance_report_by_id(self, report_id: str) -> PerformanceReport:
        stmt = select(PerformanceReport).where(PerformanceReport.report_id == report_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_performance_report(self, report_id: str, report_data: PerformanceReportUpdate) -> PerformanceReport:
        try:
            report = await self.get_performance_report_by_id(report_id)
            if not report:
                return None
            for key, value in report_data.dict(exclude_unset=True).items():
                setattr(report, key, value)
            await self.db_session.flush()
            await self.db_session.commit()
            await self.db_session.refresh(report)
            return report
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error updating performance report: {str(e)}")
            raise Exception(f"Failed to update performance report: {str(e)}")

    async def delete_performance_report(self, report_id: str) -> bool:
        try:
            report = await self.get_performance_report_by_id(report_id)
            if not report:
                return False
            await self.db_session.delete(report)
            await self.db_session.flush()
            await self.db_session.commit()
            return True
        except Exception as e:
            await self.db_session.rollback()
            print(f"Error deleting performance report: {str(e)}")
            raise Exception(f"Failed to delete performance report: {str(e)}")
