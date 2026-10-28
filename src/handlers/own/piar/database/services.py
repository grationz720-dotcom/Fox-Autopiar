from src.handlers.own.piar.database.model import AutoSend
import asyncio
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from database_tools.core import async_session_maker

async def create_autosend(text: str, for_time: int):
    if for_time >= 18000 or for_time < 300:
        for_time = 1800

    if len(text) >= 4096:
        text = text[:4092] + '...'

    async with async_session_maker() as session:
        new_send = AutoSend(text=text, for_time=for_time, waiting_for_decision=True, decision_text='Не определено')

        session.add(new_send)
        await session.commit()
        await session.refresh(new_send)
        
        session.expunge(new_send) 
        
    return new_send

async def set_decision(decision_status: bool, text: str = 'Не определено'):
    try:
        async with async_session_maker() as session:
            statement = select(AutoSend).where(AutoSend.waiting_for_decision == True)
            result = await session.exec(statement)
            autosend_obj = result.first()

            if autosend_obj:
                autosend_obj.waiting_for_decision = decision_status
                autosend_obj.decision_text = text
                await session.commit()
                await session.refresh(autosend_obj)
                session.expunge(autosend_obj)

            return autosend_obj

    except Exception as e:
        print(f'Ошибка при обновлении решения в БД: {e}')
        return None
        
    except Exception as e:
        print(f'Произошла ошибка при чтении/записи решения: {e}')

async def delete_autosend(id: int):
    try:
        async with async_session_maker() as session:
            statement = select(AutoSend).where(AutoSend.id == id)
            result = await session.exec(statement)
            autosend_obj = result.first()

            if autosend_obj:
                await session.delete(autosend_obj)
                await session.commit()
                return True
            
            print(f"Запись с id {id} не найдена в базе данных.")
            return False

    except Exception as e:
        print(f'Ошибка при удалении из БД: {e}')
        return False