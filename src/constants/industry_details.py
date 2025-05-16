"""
This module contains industry-specific details and contextual information
that will be used to enhance the prompt templates.
"""

INDUSTRY_DETAILS = {
    "food_and_beverage": """
    Industry-Specific Context for Food & Beverage:
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
    - Product quality and consistency
    """,
    
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
}

ROLE_DETAILS = {
    "plant_manager": """
    Role-Specific Context for Plant Manager:
    - Overall plant operations management and optimization
    - Production efficiency and throughput improvement
    - Team leadership and development
    - Budget management and cost control
    - Safety and compliance oversight
    - Quality assurance and control
    - Resource allocation and optimization
    - Performance metrics and KPIs
    - Strategic planning and execution
    - Stakeholder communication
    - Process improvement initiatives
    - Equipment and facility management
    - Inventory control
    - Environmental compliance
    - Emergency response planning
    """,
    
    "procurement": """
    Role-Specific Context for Procurement:
    - Supplier relationship management and development
    - Cost negotiation and optimization
    - Inventory management and control
    - Supply chain coordination and optimization
    - Quality standards enforcement
    - Contract management and compliance
    - Market analysis and trends
    - Risk assessment and mitigation
    - Sustainability considerations
    - Compliance with regulations
    - Vendor selection and evaluation
    - Cost reduction strategies
    - Material sourcing
    - Supplier performance monitoring
    - Strategic sourcing initiatives
    """,
    
    "maintenance": """
    Role-Specific Context for Maintenance:
    - Equipment reliability and uptime
    - Preventive maintenance programs
    - Troubleshooting and repairs
    - Safety protocols and compliance
    - Spare parts management
    - Maintenance scheduling and planning
    - Technical documentation
    - Team training and development
    - Cost control and optimization
    - Performance optimization
    - Predictive maintenance
    - Equipment upgrades
    - Maintenance software systems
    - Safety training
    - Emergency response
    """
}

EXPERIENCE_LEVEL_DETAILS = {
    "junior": """
    Experience Level Context for Junior:
    - Basic operational knowledge and understanding
    - Learning and development focus
    - Supervised decision-making
    - Task execution and completion
    - Process understanding and following
    - Team collaboration and support
    - Technical skill building
    - Safety awareness and compliance
    - Quality standards adherence
    - Communication basics
    - Problem-solving fundamentals
    - Equipment operation
    - Documentation basics
    - Team coordination
    - Quality control basics
    """,
    
    "mid": """
    Experience Level Context for Mid-Level:
    - Operational expertise and efficiency
    - Independent decision-making
    - Team leadership and mentoring
    - Process optimization and improvement
    - Advanced problem-solving
    - Project management
    - Technical mastery
    - Safety leadership
    - Quality improvement
    - Strategic thinking
    - Resource management
    - Performance optimization
    - Team development
    - Process innovation
    - Cross-functional coordination
    """,
    
    "senior": """
    Experience Level Context for Senior:
    - Strategic leadership and vision
    - Complex decision-making
    - Team development and mentoring
    - Process innovation and optimization
    - Advanced problem-solving
    - Program management
    - Technical excellence
    - Safety culture development
    - Quality excellence
    - Business acumen
    - Change management
    - Strategic planning
    - Performance optimization
    - Risk management
    - Stakeholder management
    """
}

MANUFACTURING_MODEL_DETAILS = {
    "self_manufacturing": """
    Self-Manufacturing Context:
    - Complete control over production processes
    - Direct quality management
    - Customization capabilities
    - Higher capital investment
    - Full operational control
    - Direct workforce management
    - In-house expertise development
    - Equipment ownership
    - Facility management
    - Process optimization
    - Quality control
    - Inventory management
    - Maintenance control
    - Cost management
    - Innovation implementation
    """,
    
    "contract_manufacturing": """
    Contract Manufacturing Context:
    - Outsourced production
    - Reduced capital investment
    - Focus on core competencies
    - Scalability options
    - Quality assurance through contracts
    - Reduced operational overhead
    - Access to specialized expertise
    - Flexible production capacity
    - Risk sharing
    - Cost predictability
    - Supply chain management
    - Quality monitoring
    - Performance metrics
    - Contract management
    - Vendor relationships
    """
}

GEOGRAPHY_DETAILS = {
    "united_states": """
    United States Manufacturing Context:
    - Compliance with US regulations (OSHA, EPA, FDA)
    - US market standards and requirements
    - Labor laws and regulations
    - Environmental compliance
    - Safety standards
    - Quality requirements
    - Import/export regulations
    - Tax considerations
    - Market dynamics
    - Consumer preferences
    - Industry standards
    - Regulatory framework
    - Market competition
    - Supply chain considerations
    - Business practices
    """
} 