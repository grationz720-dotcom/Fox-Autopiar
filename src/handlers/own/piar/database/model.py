from database_tools.core import BaseModel
from sqlmodel import Field

class AutoSend(BaseModel, table=True):
    __tablename__ = 'AutoSend'

    id: int = Field(
        primary_key=True,
        unique=True,
        description='ID для конкретного цикла авто-рассылки.'
    )
    text: str = Field(
        unique=True,
        description='Текст для авто-рассылки.'
    )
    for_time: int = Field(
        default=1800,
        description='Сколько времени пиарить (в секундах).'
    )
    waiting_for_decision: bool = Field(
        default=True,
        description='Проходит ли модерация.'
    )
    decision_text: str = Field(
        default='Нет причины',
        description='Текст, который отправила модерация в ответ на заявку.'
    )