from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Optional
from datetime import datetime

class AICoachingDAL:
    def __init__(self):
        # Initialize LLM for coaching analysis
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key="AIzaSyCPnG_Yyctqo-QX47IWlkQ8Aoz1-mgCXV0"
        )
        
        # Upstash Redis configuration
        self.UPSTASH_URL = "https://warm-koi-14565.upstash.io"
        self.UPSTASH_TOKEN = "ATjlAAIjcDE5OGE0ZGVjYmE5OTA0OTcyOGUxYzBlNTMxOGEyZWIzY3AxMA"

    def _get_chat_history(self, user_id: str, session_id: str) -> UpstashRedisChatMessageHistory:
        """Get chat history from Upstash Redis"""
        return UpstashRedisChatMessageHistory(
            url=self.UPSTASH_URL,
            token=self.UPSTASH_TOKEN,
            session_id=f"user:{user_id}:session:{session_id}"
        )

    async def get_session_messages(self, user_id: str, session_id: str) -> List[Dict]:
        """Retrieve all messages from a chat session"""
        try:
            chat_history = self._get_chat_history(user_id, session_id)
            messages = chat_history.messages
            
            # Convert messages to dictionary format
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    role = "user" if msg.type == "human" else "assistant"
                    formatted_messages.append({
                        "role": role,
                        "content": msg.content,
                        "timestamp": getattr(msg, 'timestamp', datetime.utcnow().isoformat())
                    })
            
            return formatted_messages
            
        except Exception as e:
            print(f"Error retrieving session messages: {str(e)}")
            return []

    async def generate_coaching_feedback(self, user_id: str, session_id: str) -> Dict:
        """Generate comprehensive coaching feedback for a conversation"""
        try:
            # Retrieve current messages
            messages = await self.get_session_messages(user_id, session_id)
            
            if not messages:
                return {
                    "status": "no_data",
                    "message": "No conversation data found for this session.",
                    "coaching_feedback": None
                }

            if len(messages) < 2:
                return {
                    "status": "insufficient_data",
                    "message": "Not enough conversation data for coaching analysis. At least 2 messages required.",
                    "coaching_feedback": None
                }

            # Format conversation for analysis
            conversation_text = ""
            for msg in messages:
                role = "User" if msg["role"] == "user" else "AI Assistant"
                conversation_text += f"{role}: {msg['content']}\n"

            # Universal coaching prompt
            coaching_prompt = f"""
You are an expert sales coach analyzing a real sales conversation. Based on the conversation below, provide specific, actionable coaching feedback.

Conversation:
{conversation_text}

Provide coaching feedback specifically focused on these new messages. Analyze:

1. Immediate Response Quality: How well did the salesperson handle the customer's latest input?
2. Opportunity Assessment: What opportunities were created or missed in these new exchanges?
3. Communication Effectiveness: Rate the clarity, persuasiveness, and professionalism of recent responses
4. Next Action Items: Specific suggestions based on the customer's latest responses

Keep your feedback:
- Focused specifically on the new messages from the last 15 seconds
- Actionable and immediately applicable
- Brief but insightful (IMPORTANT: respond in between 20 to 30 words only for each section)
- Based on what just happened in the conversation

Provide your coaching feedback:
"""

            # Get coaching response from LLM
            response = await self.llm.ainvoke([{"role": "user", "content": coaching_prompt}])
            
            return {
                "status": "success",
                "session_info": {
                    "user_id": user_id,
                    "session_id": session_id,
                    "message_count": len(messages),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                "coaching_feedback": response.content,
                "conversation_summary": {
                    "total_messages": len(messages),
                    "user_messages": len([m for m in messages if m["role"] == "user"]),
                    "assistant_messages": len([m for m in messages if m["role"] == "assistant"]),
                    "last_message_time": messages[-1]["timestamp"] if messages else None
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating coaching feedback: {str(e)}",
                "coaching_feedback": None
            }