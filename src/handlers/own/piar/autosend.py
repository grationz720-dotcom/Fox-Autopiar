import asyncio
import random
from vkbottle.api import API
from vkbottle.modules import logger

send_lock = asyncio.Lock()

async def start_auto_send(bot: API, text: str):
    async with send_lock:
        logger.info("Запущен новый поток авторассылки рекламы.")
        
        while True:
            try:
                conversations = await bot.messages.get_conversations(count=200)
                items = conversations.items

                if not items:
                    logger.warning("Бот не состоит ни в одной беседе/диалоге. Ожидание 2.5 минуты...")
                    await asyncio.sleep(150)
                    continue

                logger.info(f"Начинаем круг рассылки по {len(items)} чатам...")

                for item in items:
                    peer_id = item.conversation.peer_id
                    
                    if not item.conversation.can_write.allowed:
                        continue

                    try:
                        await bot.messages.send(
                            peer_id=peer_id,
                            message=text,
                            random_id=random.randint(1, 1000000000)
                        )
                        logger.info(f"Реклама успешно отправлена в чат {peer_id}")
                        
                    except Exception as chat_err:
                        logger.error(f"Не удалось отправить сообщение в {peer_id}: {chat_err}")
                    
                    await asyncio.sleep(1.5)

                logger.info("Круг рассылки завершен. Засыпаем на 2.5 минуты...")
                await asyncio.sleep(150)

            except Exception as global_err:
                logger.critical(f"Критическая ошибка в главном цикле рассылки: {global_err}")
                await asyncio.sleep(10)