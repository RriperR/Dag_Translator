from sqlalchemy import select, update, or_

from database.models import async_session
from database.models import User, DictionaryEntry


async def set_user(tg_id) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, mode="simple"))
            await session.commit()


async def set_mode(tg_id, mode: str) -> None:
    async with async_session() as session:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(mode=mode)
        )
        await session.commit()



async def get_entries(search_term: str):
    async with async_session() as session:
        stmt = select(DictionaryEntry).where(
            or_(
                DictionaryEntry.word.ilike(f"%{search_term}%"),
                DictionaryEntry.translation.ilike(f"%{search_term}%")
            )
        )
        result = await session.execute(stmt)
        entries = result.scalars().all()

        if not entries:
            return []

        response_lines = []
        for entry in entries:
            line = f"{entry.word} - {entry.translation}"
            if entry.examples:
                line += f"\n\n{entry.examples}"
            response_lines.append(line)

        return response_lines
