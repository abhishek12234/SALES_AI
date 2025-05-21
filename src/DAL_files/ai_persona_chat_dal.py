from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import UpstashRedisChatMessageHistory

from schemas.ai_personas_schemas import ManufacturingModelEnum, ExperienceLevelEnum,PlantSizeImpactEnum, RoleEnum
from langchain_groq import ChatGroq
from pydantic import BaseModel
import uuid

class ChatWithPersonaRequest(BaseModel):
    industry: str
    manufacturing_model: ManufacturingModelEnum
    experience_level: ExperienceLevelEnum
    role: RoleEnum
    intraction_mode_id: str
    geography: str
    plant_size_impact: PlantSizeImpactEnum

llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key="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",
    temperature=0.1)


plant_adaptation_guidelines = {
    "Industry Details": {
        "food_and_beverage": """Industry-Specific Context for Food & Beverage:
    - Focus on food safety and hygiene standards (HACCP, FDA, ISO 22000)
    - Emphasis on temperature control and monitoring systems
    - Importance of shelf-life management and product freshness
    - Need for traceability in supply chain (from farm to fork)
    - Compliance with FDA regulations and food safety standards
    - Quality control in food processing and packaging
    - Sanitation and cleaning protocols (CIP, SIP systems)
    - Allergen management and cross-contamination prevention
    - Cold chain logistics and temperature monitoring
    - Packaging requirements for food safety and preservation
    - Sustainability in food production and packaging
    - Waste management and reduction strategies
    - Energy efficiency in food processing
    - Water conservation and treatment
    - Product quality and consistency""",
    
    "packaging": """
    Industry-Specific Context for Packaging:
    - Material selection and sustainability (recyclable, biodegradable)
    - Design for manufacturability and efficiency
    - Quality control in printing and finishing processes
    - Supply chain optimization and logistics
    - Waste reduction and recycling initiatives
    - Cost-effective production methods
    - Custom packaging solutions for different products
    - Regulatory compliance (FDA, EU standards)
    - Brand consistency and visual identity
    - Environmental impact considerations
    - Automation in packaging processes
    - Quality assurance and testing
    - Inventory management
    - Equipment maintenance and reliability
    - Safety standards and protocols
    """
    },
    
    "Role": {
        "plant_manager": "Plant Manager Concerns: Overall operational impact and production disruption. Staff resources required for implementation. Total cost of ownership including maintenance and support. Impact on key KPIs (OEE, quality metrics, safety). Training requirements and learning curve for staff. Integration with existing workflows and procedures. Tariff implications for overall facility budget and operational costs.",
        
        "maintenance_manager": "Maintenance Manager Concerns: Spare parts availability and inventory requirements, especially with tariff considerations. Technical support and service response times. Maintenance requirements and preventive maintenance schedules. Reliability data and expected downtime. Integration with existing equipment and systems. Training for maintenance technicians. Vulnerability to parts shortages due to international trade restrictions.",
        
        "production_manager": "Production Manager Concerns: Impact on production schedules and throughput. Changeover time and flexibility. Operator training and skill requirements. Product quality and consistency impacts. Cleaning and sanitation procedures. Line efficiency and speed capabilities. Production disruption risks due to tariff-related parts delays.",
        
        "quality_manager": "Quality Manager Concerns: Food safety and compliance implications. Validation and verification procedures. Product consistency and quality control. Documentation and record-keeping requirements. Cleaning and sanitation validation. Foreign material prevention and detection. Compliance with changing regulations if parts must be substituted due to tariffs."
    },
    
    "Manufacturing Model Details": {
        "self_manufacturing": "Self-Manufacturer Closing Concerns: Greater focus on brand quality consistency during transition. Higher concern about consumer perception and product quality. More emphasis on marketing requirements and packaging integrity. Stronger focus on product differentiation capabilities. More direct questions about impact on product characteristics. Greater attention to sensory qualities and consistency. Higher sensitivity to tariff impacts on consumer pricing and competitiveness.",
        
        "contract_manufacturing": "Contract Manufacturer Closing Concerns: Greater focus on flexibility to handle diverse client requirements. Higher emphasis on changeover efficiency and multi-product capabilities. More concern about meeting client specifications consistently. Stronger focus on cost efficiency and competitive pricing. More complex stakeholder dynamics including client approvals. Greater attention to capacity utilization and throughput metrics. Higher sensitivity to tariff impacts on tight margin contracts with fixed pricing."
    },
    
    "Plant Size Considerations": {
        "small": "Small Plant Considerations (< 50 employees): Higher sensitivity to cash flow and capital expenditure. Greater concern about implementation resource constraints. More emphasis on multi-purpose functionality and versatility. Higher impact of any production downtime during implementation. More direct and expedited decision-making process. Greater concern about technical support and self-sufficiency. Higher vulnerability to tariff fluctuations due to limited financial buffers.",
        
        "medium": "Medium Plant Considerations (50-200 employees): Balanced concern for cost and capability. Structured approval process involving department heads. More emphasis on scalability and future expansion capacity. Moderate redundancy capabilities during implementation. Split focus between strategic and operational considerations. Stronger need for implementation planning and coordination. Moderate concern about tariff impacts with some mitigation capability.",
        
        "large": "Large Plant Considerations (>200 employees): Complex approval process with multiple stakeholders. Greater emphasis on enterprise standards and integration. Stronger focus on documentation and formal justification. Higher expectation for comprehensive implementation support. More extensive training requirements across shifts. Greater attention to corporate alignment and standardization. Sophisticated tariff risk assessment as part of procurement process."
    }
}



# You should inject or configure your LLM instance elsewhere and pass it in
class AIPersonaChatDAL:
    def __init__(self, llm):
        self.llm = llm

    async def chat_with_persona(self,session_id:str, user_id:str,persona_id:str, persona_prompt:str,persona_data:ChatWithPersonaRequest):
        # Set up Upstash Redis for chat history
        UPSTASH_URL = "https://dynamic-buzzard-35275.upstash.io"
        UPSTASH_TOKEN = "AYnLAAIjcDFiMWYzZDAxZDE2ZTk0MzE1OTFiMWJhNjEyNDVlNGU4ZXAxMA"

        history = UpstashRedisChatMessageHistory(
            url=UPSTASH_URL,
            token=UPSTASH_TOKEN,
            session_id=f"user:{user_id}:session:{session_id}:persona:{persona_id}"
        )

        # Validate and get industry details
        industry_key = persona_data.industry.lower().replace(" ", "_")
        industry_details = plant_adaptation_guidelines["Industry Details"].get(
            industry_key,
            "General manufacturing industry context and considerations."
        )

        # Prepare the prompt template
        system_template = persona_prompt.format(
            industry_details=plant_adaptation_guidelines["Industry Details"][persona_data.industry],
            industry=persona_data.industry,
            experience_level=persona_data.experience_level,
            role_details=plant_adaptation_guidelines["Role"][persona_data.role],
            manufacturing_model_details=plant_adaptation_guidelines["Manufacturing Model Details"][persona_data.manufacturing_model],
            plant_size_considerations=plant_adaptation_guidelines["Plant Size Considerations"][persona_data.plant_size_impact],
            role=persona_data.role,
            plant_size_impact=persona_data.plant_size_impact,
            manufacturing_model=persona_data.manufacturing_model
        )
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])

        # Set up memory with chat history
        memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=history, return_messages=True)

        # Create the conversation chain
        conversation_chain = ConversationChain(memory=memory, prompt=prompt, llm=self.llm)

        # Get the response
        teacher_response = conversation_chain.invoke({"input": persona_data.user_input})

        return teacher_response["response"]
