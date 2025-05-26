from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models.performance_reports import PerformanceReport
from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import json
from datetime import datetime
import os
from sqlalchemy import select

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
        self.UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "https://warm-koi-14565.upstash.io")
        self.UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "ATjlAAIjcDE5OGE0ZGVjYmE5OTA0OTcyOGUxYzBlNTMxOGEyZWIzY3AxMA")

    async def get_session_history(self, user_id: str, session_id: str) -> list:
        """Get conversation history from Upstash using the same format as chat system"""
        try:
            history = UpstashRedisChatMessageHistory(
                url=self.UPSTASH_URL,
                token=self.UPSTASH_TOKEN,
                session_id=f"user:{user_id}:session:{session_id}"
            )
            
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

    async def generate_performance_report(self, user_id: str, session_id: str) -> PerformanceReport:
        """Generate performance report from chat history"""
        try:
            # Get chat history
            chat_history = await self.get_session_history(user_id, session_id)
            if not chat_history:
                raise Exception("No chat history found for this session")

            # Prepare chat history for analysis
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in chat_history
            ])

            # Create system prompt template
            system_prompt = """You are an expert sales coach analyzing a conversation between a sales representative and a customer in the manufacturing industry. Your task is to evaluate the sales representative's performance across multiple dimensions and provide actionable coaching feedback.

            Evaluate the sales representative on these key closing skills:

1. OBJECTION HANDLING:
   - Effectively addressing each concern without dismissing its importance
   - Providing specific, relevant evidence to overcome objections
   - Distinguishing between real obstacles and stalling tactics
   - Using objections as opportunities to reinforce value
   - Maintaining positive momentum despite challenges
   - Addressing tariff concerns with realistic mitigation strategies

2. VALUE REINFORCEMENT:
   - Connecting solution benefits to your specific operational challenges
   - Quantifying benefits in terms relevant to your KPIs
   - Differentiating from alternatives in meaningful ways
   - Presenting convincing ROI and payback period calculations
   - Emphasizing total value beyond just purchase price
   - Demonstrating value stability despite potential tariff fluctuations

3. RISK MITIGATION:
   - Providing credible assurances about implementation and disruption
   - Outlining specific support and contingency plans
   - Addressing warranty and performance guarantee concerns
   - Presenting realistic timelines and resource requirements
   - Offering references or evidence of successful similar implementations
   - Presenting effective strategies for managing tariff-related risks

4. NEGOTIATION SKILL:
   - Finding win-win solutions to contractual concerns
   - Offering creative alternatives to overcome financial obstacles
   - Knowing when to be firm and when to be flexible
   - Maintaining value focus rather than just price focus
   - Finding appropriate trade-offs rather than one-sided concessions
   - Negotiating fair tariff protection provisions

5. COMMITMENT SECURING:
   - Recognizing buying signals and advancing appropriately
   - Proposing clear, specific next steps
   - Securing appropriate commitment given the conversation progress
   - Creating urgency without using high-pressure tactics
   - Effectively handling final resistance to commitment
   - Addressing remaining tariff concerns in a way that enables moving forward

6. TARIFF KNOWLEDGE & MITIGATION ASSESSMENT:
   - Demonstrating understanding of tariff impacts on F&B equipment and parts
   - Presenting credible strategies for mitigating tariff-related risks
   - Offering appropriate contractual protections against future tariff increases
   - Showing awareness of domestic vs. international sourcing implications
   - Providing relevant examples of how other customers have managed tariff issues
   - Balancing transparency about tariff risks with confidence in solutions

You must respond with ONLY a valid JSON object containing the following fields (all required):
- overall_score (integer 0-100)
- engagement_level (integer 0-100)
- communication_level (integer 0-100)
- objection_handling (integer 0-100)
- adaptability (integer 0-100)
- persuasiveness (integer 0-100)
- create_interest (integer 0-100)
- sale_closing (integer 0-100)
- discovery (integer 0-100)
- cross_selling (integer 0-100)
- solution_fit (integer 0-100)
- coaching_summary (string with detailed feedback)

Do not include any text before or after the JSON object."""

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

            # Create performance report
            report_data = PerformanceReportCreate(
                session_id=session_id,
                overall_score=analysis["overall_score"],
                engagement_level=analysis["engagement_level"],
                communication_level=analysis["communication_level"],
                objection_handling=analysis["objection_handling"],
                adaptability=analysis["adaptability"],
                persuasiveness=analysis["persuasiveness"],
                create_interest=analysis["create_interest"],
                sale_closing=analysis["sale_closing"],
                discovery=analysis["discovery"],
                cross_selling=analysis["cross_selling"],
                solution_fit=analysis["solution_fit"],
                coaching_summary=analysis["coaching_summary"]
            )

            # Create and return the report
            return await self.create_performance_report(report_data)

        except Exception as e:
            print(f"Error generating performance report: {str(e)}")
            raise Exception(f"Failed to generate performance report: {str(e)}")

    async def create_performance_report(self, report_data: PerformanceReportCreate) -> PerformanceReport:
        try:
            new_report = PerformanceReport(
                session_id=report_data.session_id,
                overall_score=report_data.overall_score,
                engagement_level=report_data.engagement_level,
                communication_level=report_data.communication_level,
                objection_handling=report_data.objection_handling,
                adaptability=report_data.adaptability,
                persuasiveness=report_data.persuasiveness,
                create_interest=report_data.create_interest,
                sale_closing=report_data.sale_closing,
                discovery=report_data.discovery,
                cross_selling=report_data.cross_selling,
                solution_fit=report_data.solution_fit,
                coaching_summary=report_data.coaching_summary,
            )
            self.db_session.add(new_report)
            await self.db_session.flush()
            await self.db_session.commit()  # Add explicit commit
            await self.db_session.refresh(new_report)
            return new_report
        except Exception as e:
            await self.db_session.rollback()  # Rollback on error
            print(f"Error creating performance report: {str(e)}")
            raise Exception(f"Failed to create performance report: {str(e)}")

    async def get_performance_report_by_id(self, report_id: str) -> PerformanceReport:
        stmt = select(PerformanceReport).where(PerformanceReport.report_id == report_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    # async def get_reports_by_session_id(self, session_id: str) -> list[PerformanceReport]:
    #     result = await self.db_session.execute(
    #         self.db_session.query(PerformanceReport).filter(PerformanceReport.session_id == session_id)
    #     )
    #     return result.scalars().all()

    async def update_performance_report(self, report_id: str, report_data: PerformanceReportUpdate) -> PerformanceReport:
        try:
            report = await self.get_performance_report_by_id(report_id)
            if not report:
                return None
            for key, value in report_data.dict(exclude_unset=True).items():
                setattr(report, key, value)
            await self.db_session.flush()
            await self.db_session.commit()  # Add explicit commit
            await self.db_session.refresh(report)
            return report
        except Exception as e:
            await self.db_session.rollback()  # Rollback on error
            print(f"Error updating performance report: {str(e)}")
            raise Exception(f"Failed to update performance report: {str(e)}")

    async def delete_performance_report(self, report_id: str) -> bool:
        try:
            report = await self.get_performance_report_by_id(report_id)
            if not report:
                return False
            await self.db_session.delete(report)
            await self.db_session.flush()
            await self.db_session.commit()  # Add explicit commit
            return True
        except Exception as e:
            await self.db_session.rollback()  # Rollback on error
            print(f"Error deleting performance report: {str(e)}")
            raise Exception(f"Failed to delete performance report: {str(e)}")