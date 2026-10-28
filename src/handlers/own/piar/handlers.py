from vkbottle.bot import BotLabeler, Message
from vkbottle import BuiltinStateDispenser
from src.handlers.own.piar.database import services, model
import src.handlers.own.keyboard
import asyncio
from src.handlers.own.piar.piarfsmstate import AutoSendState
from dotenv import load_dotenv
import os

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
        message.from_id, 
        AutoSendState.WAITING_FOR_TIME, 
        payload={"text": message.text} 
    )
    await message.answer('Отправьте время в секундах сколько будет продолжаться рассылка.')

@bot.message(state=AutoSendState.WAITING_FOR_TIME)
async def handle_waiting_for_time(message: Message):
    if not message.text.isdigit():
        return await message.answer("Введите время цифрами (например, 600)!")

    for_time = int(message.text)

    state_data = await state_dispenser.get(message.peer_id)
    
    if not state_data or "text" not in state_data.payload:
        await state_dispenser.delete(message.peer_id)
        return await message.answer("Произошла ошибка. Начните заполнение заявки заново.")

    saved_text = state_data.payload["text"]

    await services.create_autosend(text=saved_text, for_time=for_time)

    await state_dispenser.delete(message.peer_id)

    await message.answer('✅ Заявка на пиар успешно создана и сохранена в базу данных!\n\n⏳ Ожидайте решения администрации.')

    await message.ctx_api.messages.send(
        peer_id=int(os.environ.get('admin_chat_id', None)),
        message=f'[@all|Администрация]! Пришла новая заявка на пиар.\n\nТекст: "{saved_text}"',
        random_id=0
    )