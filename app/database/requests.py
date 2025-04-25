from sqlalchemy import select, update, or_, func

from database.models import async_session, User, DictionaryEntry, UserEntry


async def set_user(tg_id: int) -> None:
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


async def get_users_entries(search_term: str) -> list[str]:
    term = search_term.strip().lower()

    async with async_session() as session:
        stmt = select(UserEntry).where(
            or_(
                func.lower(term) == func.any_(func.string_to_array(func.lower(UserEntry.words), '; ')),
                func.lower(term) == func.any_(func.string_to_array(func.lower(UserEntry.translations), '; '))
            )
        )

        result = await session.execute(stmt)
        entries = result.scalars().all()  # ← возвращает список объектов DictionaryEntry

        response = []
        for entry in entries:
            text = f"------- перевод от анонимного пользователя ------- \n\n<b>{entry.words}</b> - {entry.translations}"
            if entry.examples:
                text += f"\n\n{entry.examples}"
            if entry.notes:
                text += f"\n\n{entry.notes}"
            response.append(text)

        return response


async def add_entry(word: str, translation: str, tg_id: int, examples: str = None, notes: str = None) -> None:
    async with async_session() as session:
        # Найти пользователя по tg_id
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if user is None:
            raise ValueError("Пользователь не найден. Пожалуйста, зарегистрируйтесь.")

        entry = UserEntry(
            words=word,
            translations=translation,
            examples=examples,
            notes=notes,
            user_id=user.id
        )

        session.add(entry)
        await session.commit()


async def update_user_info(tg_id: int, username: str | None, first_name: str | None, last_name: str | None) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            updated = False
            if user.username != username:
                user.username = username
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if updated:
                await session.commit()
