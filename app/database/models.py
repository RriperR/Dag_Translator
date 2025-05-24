import os

from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from sqlalchemy import BigInteger, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bot_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")


engine = create_async_engine(f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(MOSCOW_TZ))
    mode: Mapped[str] = mapped_column(String(12), default='simple')
    language: Mapped[str] = mapped_column(String(32), default='lezginski')


class AbstractEntry(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    words: Mapped[str] = mapped_column(Text, nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)
    translations: Mapped[str] = mapped_column(Text, nullable=False)
    keytranslations: Mapped[str] = mapped_column(Text, nullable=False)
    examples: Mapped[str] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    original: Mapped[str] = mapped_column(Text, nullable=True)


class LezginskiEntry(AbstractEntry):
    __tablename__ = "lezginski_entries"

class KubachinskiEntry(AbstractEntry):
    __tablename__ = "kubachinski_entries"


class UserEntry(Base):
    __tablename__ = 'user_entries'

    id: Mapped[int] = mapped_column(primary_key=True)
    words: Mapped[str] = mapped_column(Text)
    translations: Mapped[str] = mapped_column(Text)
    examples: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(backref="user_entries")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
