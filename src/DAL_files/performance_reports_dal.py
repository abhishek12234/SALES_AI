from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json
from datetime import datetime
import os
from sqlalchemy import select
from dotenv import load_dotenv
from config import settings
from DAL_files.sessions_dal import SessionDAL
from fastapi import HTTPException

session_service = SessionDAL()

load_dotenv()

class PerformanceReportDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # Initialize Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Using the same model as chat system
            google_api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCD5cJgxk11YYhM8CeVAvNzmkhpLUaVes8"),
            temperature=0.1
        )
        # Initialize Upstash Redis URL and token


    async def get_session_history(self, user_id: str, session_id: str) -> list:
        """Get conversation history from Upstash using the same format as chat system"""
        try:
            history = UpstashRedisChatMessageHistory(
                url=settings.upstash_redis_rest_url,
                token=settings.upstash_redis_rest_token,
                session_id=f"user:{user_id}:session:{session_id}"
                
            )
            print("history",history,history.messages,"history")
            
            # Get all messages from the history
            messages = history.messages
            if not messages:
                return []

            # Convert messages to the expected format
            return [
                {
                    "role": "assistant" if msg.type == "ai" else "human",
                    "content": msg.content
                }
                for msg in messages
            ]

        except Exception as e:
            print(f"Error retrieving session history: {str(e)}")
            return []

    async def generate_performance_report(self, user_id: str, session_id: str, prompt_template: str) :
        """Generate performance report from chat history"""
        try:
            # Check if a report already exists for this session
            # Get chat history
            chat_history = await self.get_session_history("01234f0f-1612-43d8-95ad-10541f596be9", "b4dcc278-00d7-47fa-a0bd-6a0cb2dba52d")
            if not chat_history:
                raise Exception("No chat history found for this session")

            # Prepare chat history for analysis
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in chat_history
            ])

            # Create system prompt template
            system_prompt = prompt_template

            # Create human prompt template
            human_prompt = """Analyze this conversation and provide a performance evaluation:

                        {conversation}

                        Remember to:
                        1. Score each category from 0-100
                        2. Calculate overall score as average of all categories
                        3. Provide specific examples in coaching summary
                        4. Return ONLY the JSON object"""

            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(human_prompt)
            ])

            # Format the prompt
            formatted_prompt = prompt.format_messages(conversation=conversation_text)

            # Get analysis from LLM
            response = await self.llm.ainvoke(formatted_prompt)
            
            if not response or not response.content:
                raise Exception("Empty response received from LLM")
            
            # Debug logging
            print("Raw LLM Response:", repr(response.content))
            print("Response type:", type(response.content))
            
            try:
                # Try to parse the response content as JSON
                content = response.content.strip()
                # Remove any markdown code block markers if present
                content = content.replace("```json", "").replace("```", "").strip()
                analysis = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON response from LLM. Raw content: {repr(content)}")
                raise Exception(f"Invalid response format from LLM: {str(e)}")
            
            # Validate required fields and their types
            required_fields = {
                "overall_score": int,
                "engagement_level": int,
                "communication_level": int,
                "objection_handling": int,
                "adaptability": int,
                "persuasiveness": int,
                "create_interest": int,
                "sale_closing": int,
                "discovery": int,
                "cross_selling": int,
                "solution_fit": int,
                "coaching_summary": str
            }
            
            # Check if all required fields are present and have correct types
            for field, field_type in required_fields.items():
                if field not in analysis:
                    raise Exception(f"Missing required field in LLM response: {field}")
                if not isinstance(analysis[field], field_type):
                    raise Exception(f"Invalid type for field {field}. Expected {field_type.__name__}, got {type(analysis[field]).__name__}")
                if field_type == int and not (0 <= analysis[field] <= 100):
                    raise Exception(f"Value for {field} must be between 0 and 100")



            # Create and return the report
            return analysis

        except Exception as e:
            print(f"Error generating performance report: {str(e)}")
            raise Exception(f"Failed to generate performance report: {str(e)}")



    async def get_performance_report_by_user_session(self, session_id: str, user_id: str) :
        session_data = await session_service.get_session_by_id(session_id, self.db_session)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        if not session_data.performance_report:
            raise HTTPException(status_code=404, detail="Performance report not found")
        
        return session_data.performance_report
        




