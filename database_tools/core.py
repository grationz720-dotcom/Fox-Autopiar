from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv
import os

load_dotenv('scr/config/.env')

DATABASE_URL = os.environ.get('database_url', None)

if type(DATABASE_URL) != 'string':
    print('Un-correct database URL.')
    exit(0)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

class BaseModel(SQLModel):

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        description="Уникальный идентификатор записи",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Дата и время создания записи (UTC)",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Дата и время последнего обновления записи (UTC)",
    )