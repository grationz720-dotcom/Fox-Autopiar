from vkbottle.bot import Bot, Message
from src.handlers.user.database import services
from database_tools.core import async_session_maker
from src.handlers.user.database.model import User
from sqlmodel import select
import asyncio
from src.handlers.user.auth.keyboard import rules_keyboard

bot = Bot(token='vk1.a.9AqAlvzawIRQCb5_V-ghAxIj8DpWetjSLzJ8Kp0F6DVpUY-BqMS7fU05GdeVQnIr9Ey7Koz7FVgzbr_tuf2gdqzLWdm9hgJsccVmGGymkhGJPEvxLFAaJxkv6Sz-GJJmIZGebJB6KzOdC00V0aqRJGfeudGWMjFusJSjEZNv8m5pSXZUngq_6-uFScPJmpa_-HUG6BqRejFiI2sUCZ2RyA')

@bot.on.message(text='Начать', from_chat=False)
async def start_handle(message: Message):
    user = await message.get_user()
    user_name = f'{user.first_name} {user.last_name}'

    await services.create_user(
        vk_id=message.from_id, 
        profile_name=user_name, 
        roots='user'
    )
    
    await message.answer(
        message=(
            f'👋 Добро пожаловать, {user_name}! Вы успешно зарегистрированы в системе.\n\n'
            f'❗ Для продолжения работы с вами, пожалуйста, нажмите кнопку '
            f'«Принять [https://vk.ru/@foxpiarbot|правила]» ниже.'
        ),
        keyboard=rules_keyboard
    )

@bot.on.message(text='Принять правила', from_chat=False)
async def accept_rules_handler(message: Message):
    async with async_session_maker() as session:
        statement = select(User).where(User.vk_id == message.from_id)
        result = await session.exec(statement)
        user = result.scalar_or_none()
        
        if not user:
            await message.answer("⚠️ Вы не зарегистрированы в системе. Напишите «Начать».")
            return
        elif user.accepted_rules == True:
            await message.answer("⚠️ Вы уже приняли правила.")
            return
            
        user.accepted_rules = True
        
        session.add(user)
        await session.commit()
        
    await message.answer(
        message="✅ Спасибо! Вы успешно приняли правила системы.\n\n🚀 Теперь вам доступен полный функционал бота. Воспользуйтесь меню ниже."
    )