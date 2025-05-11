from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.ai_personas import AIPersona
from schemas.ai_personas_schemas import AIPersonaCreate, AIPersonaUpdate
from sqlalchemy.sql import exists

class AIPersonaDAL:
    async def persona_exists(self, persona_id: str, db_session: AsyncSession) -> bool:
        result = await db_session.execute(select(AIPersona).where(AIPersona.persona_id == persona_id))
        print(f"Persona exists: {persona_id}", '--------------------------------')
        return result.scalar_one_or_none() is not None

    async def get_all_ai_personas(self, db_session: AsyncSession) -> list[AIPersona]:
        result = await db_session.execute(select(AIPersona))
        return result.scalars().all()

    async def create_ai_persona(self, persona_data: AIPersonaCreate, db_session: AsyncSession) -> AIPersona:
        # Create a new AI Persona
        new_persona = AIPersona(
            name=persona_data.name,
            industry=persona_data.industry,
            role=persona_data.role,
            experience_level=persona_data.experience_level,
            geography=persona_data.geography,
            manufacturing_model=persona_data.manufacturing_model,
            behavioral_traits=persona_data.behavioral_traits,
            interview_results=persona_data.interview_results,
        )
        db_session.add(new_persona)
        await db_session.commit()
        await db_session.refresh(new_persona)
        return new_persona

    async def get_ai_persona_by_id(self, persona_id: str, db_session: AsyncSession) -> AIPersona:
        # Check if the persona exists
        persona = await self.persona_exists(persona_id, db_session)
        if not persona:
            return None

        return await db_session.get(AIPersona, persona_id)

    async def get_ai_persona_by_name(self, name: str, db_session: AsyncSession) -> AIPersona:
        result = await db_session.execute(
            select(AIPersona).where(AIPersona.name == name)
        )
        return result.scalar_one_or_none()

    async def get_ai_personas_by_industry(self, industry: str, db_session: AsyncSession) -> list[AIPersona]:
        result = await db_session.execute(
            select(AIPersona).where(AIPersona.industry == industry)
        )
        return result.scalars().all()

    async def update_ai_persona(self, persona_id: str, persona_data: AIPersonaUpdate, db_session: AsyncSession) -> AIPersona:
        persona = await self.get_ai_persona_by_id(persona_id, db_session)
        if not persona:
            return None
        for key, value in persona_data.model_dump(exclude_unset=True).items():
            setattr(persona, key, value)
        await db_session.commit()
        await db_session.refresh(persona)
        return persona

    async def delete_ai_persona(self, persona_id: str, db_session: AsyncSession) -> bool:
        persona = await self.get_ai_persona_by_id(persona_id, db_session)
        if not persona:
            return False
        await db_session.delete(persona)
        await db_session.commit()
        return True