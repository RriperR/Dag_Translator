from database.requests import get_user_by_tg_id, set_mode, set_language, set_user


class UserSettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSettingsManager, cls).__new__(cls)
            cls._instance._cache = {}  # user_id -> {'mode': ..., 'lang': ...}
        return cls._instance

    async def get(self, user_id: int) -> dict | None:
        if user_id in self._cache:
            return self._cache[user_id]

        user = await get_user_by_tg_id(user_id)

        if user is None:
            return None

        settings = {"mode": user.mode, "lang": user.language}

        self._cache[user_id] = settings
        print(f"cache: {self._cache}")
        return settings

    async def update(self, user_id: int, mode: str = None, lang: str = None) -> None:
        settings = await self.get(user_id)
        print(f"settings: {settings}")

        if settings is None:
            return


        # обновляем в кэше и бд
        if mode:
            self._cache[user_id]["mode"] = mode
            await set_mode(user_id, mode)

        if lang:
            self._cache[user_id]["lang"] = lang
            await set_language(user_id, lang)
