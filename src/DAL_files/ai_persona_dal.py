from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.ai_personas import AIPersona
from models.persona_produced_product import PersonaProducedProduct
from schemas.ai_personas_schemas import AIPersonaCreate, AIPersonaUpdate
from sqlalchemy.sql import exists
from fastapi import HTTPException
import random
import itertools
from datetime import datetime
from models.industries import Industry
from models.ai_roles import AIRole
from models.plant_size_impacts import PlantSizeImpact
from models.manufacturing_models import ManufacturingModel
import uuid
from sqlalchemy.orm import selectinload



class AIPersonaDAL:
    async def persona_exists(self, persona_id: str, db_session: AsyncSession) -> bool:
        result = await db_session.execute(select(AIPersona).where(AIPersona.persona_id == persona_id))
        print(f"Persona exists: {persona_id}", '--------------------------------')
        return result.scalar_one_or_none() is not None

    async def get_all_ai_personas(self, db_session: AsyncSession) -> list[AIPersona]:
        result = await db_session.execute(
            select(AIPersona)
            .options(selectinload(AIPersona.persona_products).selectinload(PersonaProducedProduct.product))
        )
        return result.scalars().all()

    async def create_ai_persona(self, persona_data: AIPersonaCreate, db_session: AsyncSession) -> AIPersona:
        persona_data_dict = persona_data.model_dump()
        # Create a new AI Persona
        new_persona = AIPersona(**persona_data_dict)
        db_session.add(new_persona)
        await db_session.commit()
        await db_session.refresh(new_persona)
        return new_persona

    async def get_ai_persona_by_id(self, persona_id: str, db_session: AsyncSession) -> AIPersona:
        # Check if the persona exists
        persona = await self.persona_exists(persona_id, db_session)
        if not persona:
            return None

        result = await db_session.execute(
            select(AIPersona)
            .options(selectinload(AIPersona.persona_products).selectinload(PersonaProducedProduct.product))
            .where(AIPersona.persona_id == persona_id)
        )
        return result.scalar_one_or_none()

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

    async def get_ai_personas_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[AIPersona]:
        """
        Get all AI personas associated with a specific user
        """
        try:
            result = await db_session.execute(
                select(AIPersona)
                .where(AIPersona.user_id == user_id)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get AI personas for user: {str(e)}")

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

    async def add_all_combinations(self, db_session: AsyncSession):
        # Fetch all existing persona names from the DB
        existing_names = set(
            (await db_session.execute(select(AIPersona.name))).scalars().all()
        )

        # Filter NAMES_LIST to only names not already in the DB
        NAMES_LIST = [
    "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Quinn", "Riley", "Skyler",
    "Jesse", "Reese", "Cameron", "Avery", "Jamie", "Kendall", "Blake", "Parker",
    "Rowan", "Emerson", "Drew", "Hayden", "Harper", "Logan", "Sawyer", "Kai",
    "Dakota", "Phoenix", "River", "Sky", "Sage", "Remy", "Sloan", "Lane",
    "John", "Sara", "Liam", "Emma", "Noah", "Olivia", "Mason", "Ava",
    "Ethan", "Mia", "Isla", "Ezra", "Leo", "Zoe", "Aria", "Theo",
    "Ivy", "Nora", "Elena", "Miles", "Ella", "Asher", "Chloe", "Lucas",
    "Nova", "Caleb", "Luna", "Henry", "Layla", "Finn", "Freya", "Jude",
    "Stella", "Owen", "Clara", "Axel", "Ruby", "Hugo", "Willow", "Silas"]
    
        available_names = [name for name in NAMES_LIST if name not in existing_names]
        random.shuffle(available_names)
        name_counter = 1

        industry_ids = list((await db_session.execute(Industry.__table__.select())).scalars())
        ai_role_ids = list((await db_session.execute(AIRole.__table__.select())).scalars())
        plant_size_impact_ids = list((await db_session.execute(PlantSizeImpact.__table__.select())).scalars())
        manufacturing_model_ids = list((await db_session.execute(ManufacturingModel.__table__.select())).scalars())
        geographies = ["US"]  # Replace with your actual geography value(s)
        experience_levels = ["junior", "mid", "senior"]

        combos = list(itertools.product(
            industry_ids,
            ai_role_ids,
            experience_levels,
            plant_size_impact_ids,
            geographies,
            manufacturing_model_ids
        ))

        added_count = 0

        for combo in combos:
            industry_id, ai_role_id, experience_level, plant_size_impact_id, geography, manufacturing_model_id = combo

            # Check if this combination already exists
            existing = await db_session.execute(
                select(AIPersona).where(
                    (AIPersona.industry_id == industry_id) &
                    (AIPersona.ai_role_id == ai_role_id) &
                    (AIPersona.experience_level == experience_level) &
                    (AIPersona.plant_size_impact_id == plant_size_impact_id) &
                    (AIPersona.geography == geography) &
                    (AIPersona.manufacturing_model_id == manufacturing_model_id)
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip if already exists

            # Get a unique name
            if available_names:
                name = available_names.pop()
            else:
                # Fallback to generated names if all are used
                while True:
                    name = f"Persona_{name_counter}"
                    name_counter += 1
                    # Ensure fallback name is unique in DB
                    name_exists = await db_session.execute(
                        select(AIPersona).where(AIPersona.name == name)
                    )
                    if not name_exists.scalar_one_or_none():
                        break

            persona = AIPersona(
                persona_id=str(uuid.uuid4()),
                name=name,
                industry_id=industry_id,
                ai_role_id=ai_role_id,
                experience_level=experience_level,
                geography=geography,
                plant_size_impact_id=plant_size_impact_id,
                manufacturing_model_id=manufacturing_model_id,
                status_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(persona)
            added_count += 1

        await db_session.commit()
        print(f"Added {added_count} new combinations (skipped existing).")