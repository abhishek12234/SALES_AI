from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory
from schemas.ai_personas_chat_schemas import ChatWithPersonaRequest
from langchain_groq import ChatGroq
from pydantic import BaseModel
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI






# You should inject or configure your LLM instance elsewhere and pass it in
class AIPersonaChatDAL:
    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",  # or "gemini-1.5-pro" for the pro model
                    google_api_key="AIzaSyCPnG_Yyctqo-QX47IWlkQ8Aoz1-mgCXV0"
                )

    async def chat_with_persona(self,session_id:str, user_id:str,persona_prompt:str,user_input:str):
        # Set up Upstash Redis for chat history
        UPSTASH_URL = "https://warm-koi-14565.upstash.io"
        UPSTASH_TOKEN = "ATjlAAIjcDE5OGE0ZGVjYmE5OTA0OTcyOGUxYzBlNTMxOGEyZWIzY3AxMA"

        history = UpstashRedisChatMessageHistory(
            url=UPSTASH_URL,
            token=UPSTASH_TOKEN,
            session_id=f"user:{user_id}:session:{session_id}"
        )

        # Set up memory with chat history
        memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=history, return_messages=True)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(persona_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])
        # Create the conversation chain
        conversation_chain = ConversationChain(memory=memory, prompt=prompt, llm=self.llm)

        # Get the response
        teacher_response = conversation_chain.invoke({"input": user_input})

        return teacher_response["response"]
