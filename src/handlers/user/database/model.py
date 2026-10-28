from sqlmodel import select, Field
from database_tools.core import BaseModel
from typing import Literal

UserRole = Literal["admin", "moderator", "user", "guest"]

class User(BaseModel, table=True):
    __tablename__ = 'User'

    vk_id: int = Field(
        primary_key=True,
        unique=True,
        description='VK ID пользователя.'
    )
    profile_name: str = Field(
        default='Неопределено',
        index=True,
        unique=True,
        description='Наименование профиля пользователя по формату "Имя Фамилия".'
    )
    roots: UserRole = Field(
        default='user',
        description='Права доступа пользователя с фиксированными вариантами выборов.',
        sa_column_kwargs={"server_default": "user"}
    )
    accepted_rules: bool = Field(
        index=True,
        default=False,
        description='Принял ли пользователь правила.'
    )
    ban_status: bool = Field(
        default=False,
        description='Заблокирован ли пользователь (эта переменная нужна только для дальнейшей бизнес-логики).'
    )