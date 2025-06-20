import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from upstash_redis import Redis
import os
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory

class AICoachingDAL:
    def __init__(self):
        # Initializekk
        self.llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16b-16b-instruct",
            groq_api_key=os.getenv("GROQ_API_KEY", "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"),
            temperature=0.3
        )

        # Initialize Upstash Redis
        self.redis = Redis(
            url=os.getenv("UPSTASH_REDIS_REST_URL", "https://warm-koi-14565.upstash.io"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN", "ATjlAAIjcDE5OGE0ZGVjYmE5OTA0OTcyOGUxYzBlNTMxOGEyZWIzY3AxMA")
        )

        # Track active monitoring sessions
        self.active_monitoring = {}

        self.UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "https://warm-koi-14565.upstash.io")
        self.UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "ATjlAAIjcDE5OGE0ZGVjYmE5OTA0OTcyOGUxYzBlNTMxOGEyZWIzY3AxMA")

    def _get_session_key(self, user_id: str, session_id: str) -> str:
        """Generate Redis key for session data"""
        return f"chat:{user_id}:{session_id}"

    def _get_coaching_key(self, user_id: str, session_id: str) -> str:
        """Generate Redis key for coaching feedback"""
        return f"coaching:{user_id}:{session_id}"

    def _get_monitoring_key(self, user_id: str, session_id: str) -> str:
        """Generate key for monitoring tracking"""
        return f"{user_id}:{session_id}"

    async def get_session_data(self, user_id: str, session_id: str):
        """
        Retrieve chat history for a session from Upstash Redis.
        Returns a list of messages in the format:
        [
            {"role": "assistant" or "human", "content": "..."},
            ...
        ]
        """
        try:
            history = UpstashRedisChatMessageHistory(
                url=self.UPSTASH_URL,
                token=self.UPSTASH_TOKEN,
                session_id=f"user:{user_id}:session:{session_id}"
            )
            messages = history.messages
            if not messages:
                return []

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

    async def analyze_new_messages(self, messages: List[Dict], previous_count: int) -> str:
        """Analyze new messages and generate coaching feedback"""
        try:
            if len(messages) <= previous_count:
                return "No new messages to analyze."

            # Get the latest 3-4 messages for context
            recent_messages = messages[max(0, len(messages) - 4):] if len(messages) > 4 else messages

            # Format conversation for analysis
            conversation_text = ""
            for msg in recent_messages:
                role = "Salesperson" if msg["role"] == "user" else "Customer"
                conversation_text += f"{role}: {msg['content']}\n"

            # Get the newest message details
            newest_message = messages[-1]
            newest_role = "Salesperson" if newest_message["role"] == "user" else "Customer"

            # Create coaching prompt focused on the new message
            coaching_prompt = f"""
You are an expert sales coach analyzing a live sales conversation. A new message just arrived.

Recent Conversation Context:
{conversation_text}

NEWEST MESSAGE:
{newest_role}: {newest_message['content']}

Provide immediate coaching feedback focusing on this new message. Analyze:

1. Response Quality: How effective was this latest message?
2. Opportunity Analysis: What opportunities were created or missed?
3. Communication Impact: Rate the effectiveness of this exchange
4. Next Steps: What should the salesperson do immediately?

Keep feedback:
- Focused on the newest message
- Actionable and specific
- Brief but insightful (30-40 words per section)
- Professional coaching tone

Provide coaching feedback:
"""

            # Get coaching response from LLM
            messages_for_llm = [{"role": "user", "content": coaching_prompt}]
            response = await self.llm.ainvoke(messages_for_llm)

            return response.content

        except Exception as e:
            return f"Error analyzing new messages: {str(e)}"

    async def save_coaching_feedback(self, user_id: str, session_id: str, feedback: str, message_count: int):
        """Save coaching feedback to Redis"""
        try:
            coaching_key = self._get_coaching_key(user_id, session_id)

            # Get existing coaching data or create new
            existing_data = self.redis.get(coaching_key)
            if existing_data:
                coaching_data = json.loads(existing_data)
            else:
                coaching_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "feedback_history": [],
                    "created_at": datetime.utcnow().isoformat()
                }

            # Add new feedback
            new_feedback = {
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_id": f"analysis_{len(coaching_data['feedback_history']) + 1}",
                "message_count_at_time": message_count,
                "trigger_type": "auto_monitoring"
            }

            coaching_data["feedback_history"].append(new_feedback)
            coaching_data["updated_at"] = datetime.utcnow().isoformat()

            # Save to Redis with expiration (24 hours)
            self.redis.set(coaching_key, json.dumps(coaching_data), ex=86400)

            print(f"Coaching feedback saved for session {session_id} at message count {message_count}")

        except Exception as e:
            print(f"Error saving coaching feedback: {str(e)}")

    async def get_coaching_feedback(self, user_id: str, session_id: str) -> List[Dict]:
        """Get coaching feedback history for a session"""
        try:
            coaching_key = self._get_coaching_key(user_id, session_id)
            coaching_data = self.redis.get(coaching_key)

            if not coaching_data:
                return []

            data = json.loads(coaching_data)
            return data.get("feedback_history", [])

        except Exception as e:
            print(f"Error getting coaching feedback: {str(e)}")
            return []

    async def start_monitoring_session(self, user_id: str, session_id: str) -> bool:
        """Initialize monitoring for a session"""
        try:
            monitoring_key = self._get_monitoring_key(user_id, session_id)

            # Check if already monitoring
            if monitoring_key in self.active_monitoring:
                return False

            # Get initial session data
            session_data = await self.get_session_data(user_id, session_id)
            if not session_data:
                return False

            initial_message_count = len(session_data)

            # Initialize monitoring state
            self.active_monitoring[monitoring_key] = {
                "user_id": user_id,
                "session_id": session_id,
                "last_message_count": initial_message_count,
                "started_at": datetime.utcnow().isoformat(),
                "status": "active",
                "task": None
            }

            # Start background monitoring task
            task = asyncio.create_task(self._monitor_session_background(user_id, session_id))
            self.active_monitoring[monitoring_key]["task"] = task

            print(f"Monitoring started for User: {user_id}, Session: {session_id}, Initial messages: {initial_message_count}")
            return True

        except Exception as e:
            print(f"Error starting monitoring: {str(e)}")
            return False

    async def _monitor_session_background(self, user_id: str, session_id: str):
        """Background task that monitors session for new messages"""
        monitoring_key = self._get_monitoring_key(user_id, session_id)

        try:
            while monitoring_key in self.active_monitoring:
                # Get current session data
                session_data = await self.get_session_data(user_id, session_id)

                if not session_data:
                    print(f"Session data not found during monitoring: {session_id}")
                    break

                current_count = len(session_data)
                last_count = self.active_monitoring[monitoring_key]["last_message_count"]

                # Check for new messages
                if current_count > last_count:
                    print(f"New messages detected! Current: {current_count}, Previous: {last_count}")

                    # Analyze new messages and generate coaching
                    coaching_feedback = await self.analyze_new_messages(session_data, last_count)

                    # Save coaching feedback
                    await self.save_coaching_feedback(user_id, session_id, coaching_feedback, current_count)

                    # Update message count
                    self.active_monitoring[monitoring_key]["last_message_count"] = current_count
                    self.active_monitoring[monitoring_key]["last_checked"] = datetime.utcnow().isoformat()

                    print(f"Coaching feedback generated for session {session_id}")

                # Wait before next check (15 seconds)
                await asyncio.sleep(15)

        except asyncio.CancelledError:
            print(f"Monitoring cancelled for session {session_id}")
        except Exception as e:
            print(f"Error during monitoring: {str(e)}")
        finally:
            # Clean up monitoring session
            if monitoring_key in self.active_monitoring:
                del self.active_monitoring[monitoring_key]
            print(f"Monitoring ended for session {session_id}")

    def stop_monitoring_session(self, user_id: str, session_id: str) -> bool:
        """Stop monitoring for a session"""
        try:
            monitoring_key = self._get_monitoring_key(user_id, session_id)

            if monitoring_key not in self.active_monitoring:
                return False

            # Cancel the background task
            monitoring_info = self.active_monitoring[monitoring_key]
            if monitoring_info["task"]:
                monitoring_info["task"].cancel()

            # Remove from active monitoring
            del self.active_monitoring[monitoring_key]

            print(f"Monitoring stopped for User: {user_id}, Session: {session_id}")
            return True

        except Exception as e:
            print(f"Error stopping monitoring: {str(e)}")
            return False

    def is_monitoring_active(self, user_id: str, session_id: str) -> bool:
        """Check if monitoring is active for a session"""
        monitoring_key = self._get_monitoring_key(user_id, session_id)
        return monitoring_key in self.active_monitoring

    def get_monitoring_status(self, user_id: str, session_id: str) -> Optional[Dict]:
        """Get monitoring status for a session"""
        monitoring_key = self._get_monitoring_key(user_id, session_id)
        return self.active_monitoring.get(monitoring_key)

    def get_all_active_monitoring(self) -> Dict:
        """Get all active monitoring sessions"""
        return self.active_monitoring.copy()