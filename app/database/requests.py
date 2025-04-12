from sqlalchemy import select, update, delete

from database.models import async_session
from database.models import User, DictionaryEntry


async def set_user(tg_id, mode: str = "simple") -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, mode=mode))
            await session.commit()
