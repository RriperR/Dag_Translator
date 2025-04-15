from sqlalchemy import select, update, or_, func

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



async def get_entries(search_term: str) -> list[str]:
    term = search_term.strip().lower()

    async with async_session() as session:
        stmt = select(DictionaryEntry).where(
            or_(
                func.lower(term) == func.any_(func.string_to_array(func.lower(DictionaryEntry.keywords), '; ')),
                func.lower(term) == func.any_(func.string_to_array(func.lower(DictionaryEntry.keytranslations), '; '))
            )
        )

        result = await session.execute(stmt)
        entries = result.scalars().all()  # ← возвращает список объектов DictionaryEntry

        response = []
        for entry in entries:
            text = f"<b>{entry.words}</b> - {entry.translations}"
            if entry.examples:
                text += f"\n\n{entry.examples}"
            if entry.grammar:
                text += f"\n\n{entry.grammar}"
            if entry.notes:
                text += f"\n\n{entry.notes}"
            response.append(text)

        return response
