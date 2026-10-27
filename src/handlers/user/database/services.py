from src.handlers.user.database.model import User
import asyncio
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from database_tools.core import async_session_maker

async def create_user(vk_id: int, profile_name: str, roots: str):
    async with async_session_maker() as session:
        user = User(vk_id=vk_id, profile_name=profile_name, roots=roots)
        session.add(user)
        
        try:
            await session.commit()
            await session.refresh(user)
            return user
        except IntegrityError:
            await session.rollback() 
            print(f"Пользователь с vk_id {vk_id} уже существует!")
            return None 