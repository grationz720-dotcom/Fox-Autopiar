import asyncio
import os
import random
from dotenv import load_dotenv
from sqlmodel import select

from vkbottle import BuiltinStateDispenser
from vkbottle.bot import BotLabeler, Message

import src.handlers.own.piar.autosend as autosend
from database_tools.core import async_session_maker
from src.handlers.own.piar.database import services
from src.handlers.own.piar.database.model import AutoSend
from src.handlers.own.piar.piarfsmstate import AutoSendState

load_dotenv('src/config/.env')

bot = BotLabeler()
state_dispenser = BuiltinStateDispenser()

@bot.message(text='Подать заявку на пиар', from_chat=False)
async def handle(message: Message):
    await state_dispenser.set(message.peer_id, AutoSendState.WAITING_FOR_TEXT)
    await message.answer("Отправьте текст для рассылки в следующем сообщении.")

@bot.message(state=AutoSendState.WAITING_FOR_TEXT, from_chat=False)
async def handle_waiting_for_text(message: Message):
    await state_dispenser.set(
        message.peer_id, 
        AutoSendState.WAITING_FOR_TIME, 
        payload={"text": message.text} 
    )
    await message.answer('Отправьте время в секундах сколько будет продолжаться рассылка.')

@bot.message(state=AutoSendState.WAITING_FOR_TIME, from_chat=False)
async def handle_waiting_for_time(message: Message):
    if not message.text.isdigit():
        return await message.answer("Введите время цифрами (например, 600)!")

    for_time = int(message.text)
    state_data = await state_dispenser.get(message.peer_id)
    
    if not state_data or "text" not in state_data.payload:
        await state_dispenser.delete(message.peer_id)
        return await message.answer("Произошла ошибка. Начните заполнение заявки заново.")

    saved_text = state_data.payload["text"]

    send_obj = await services.create_autosend(text=saved_text, for_time=for_time)

    await state_dispenser.delete(message.peer_id)
    await message.answer('✅ Заявка на пиар успешно создана и сохранена в базу данных!\n\n⏳ Ожидайте решения администрации.')

    await message.ctx_api.messages.send(
        peer_id=int(os.environ.get('admin_chat_id')),
        message=(
            f'[@all|Администрация]! Пришла новая заявка на пиар.\n\n'
            f'🆔 ID Заявки: {send_obj.id}\n'
            f'Текст: "{saved_text}"\n'
            f'Время рассылки: {for_time} сек.\n\n'
            f'Для ответа введите ".ответ {send_obj.id} <разрешить/отклонить> <текст ответа>".\n'
            f'🔴 Пользователь ждет ответа!'
        ),
        random_id=0
    )

@bot.message(text=".ответ <id_arg:int> <state_arg:str> <text_answer_arg>")
async def answer_handler_manual(message: Message, id_arg: int, state_arg: str, text_answer_arg: str):
    
    if state_arg != 'разрешить' and state_arg != 'отклонить':
        return await message.answer(f'❌ Вместо "{state_arg}" введите "разрешить" или "отклонить"!')

    async with async_session_maker() as session:
        statement = select(AutoSend).where(AutoSend.id == id_arg)
        result = await session.execute(statement)
        application = result.scalars().first()

        if not application:
            await message.answer(f'❌ Заявка с ID {id_arg} не найдена!')
            
            history_statement = select(AutoSend).order_by(AutoSend.id.desc()).limit(50)
            history_result = await session.execute(history_statement)
            apps_list = history_result.scalars().all()

            if not apps_list:
                return await message.answer('База данных рассылок пуста.')

            table_text = "📊 Последние 50 заявок в базе:\n\n"
            table_text += "🆔 ID   | 👤 User ID\n"
            table_text += "--------+-----------\n"

            for app in apps_list:
                app_id = str(app.id).ljust(6)
                user_id = str(getattr(app, 'vk_id', getattr(app, 'from_id', 'Не найден'))) 
                table_text += f"{app_id} | {user_id}\n"

            return await message.answer(table_text)

        user_peer = getattr(application, 'vk_id', getattr(application, 'from_id', None))
        
        if state_arg == 'разрешить':
            if user_peer:
                await message.ctx_api.messages.send(
                    peer_id=user_peer,
                    message=f'🟢 [id{message.from_id}|Администратор] одобрил вашу заявку!\n\nОн ответил: "{text_answer_arg}".',
                    random_id=random.randint(1, 1000000000)
                )
            
            application.wait_for_decision = False
            application.decision_text = text_answer_arg

            await session.commit()
            
            asyncio.create_task(autosend.start_auto_send(bot=message.ctx_api, text=application.text))
            
            await message.answer(f"✅ Заявка №{id_arg} разрешена. Рассылка запущена в фоновом режиме.")

        elif state_arg == 'отклонить':
            if user_peer:
                await message.ctx_api.messages.send(
                    peer_id=user_peer,
                    message=f'🔴 [id{message.from_id}|Администратор] отклонил вашу заявку.\n\nПричина: "{text_answer_arg}".',
                    random_id=random.randint(1, 1000000000)
                )
            application.wait_for_decision = False
            application.decision_text = text_answer_arg
            
            await session.commit()
            await message.answer(f"❌ Заявка №{id_arg} отклонена. Пользователь уведомлен.")