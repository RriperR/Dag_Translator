from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
import database.requests as rq
from models.UserSettings import UserSettingsManager

router = Router()

settings_manager = UserSettingsManager()

class AddWordStates(StatesGroup):
    word = State()
    translation = State()
    examples = State()
    notes = State()


@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    await rq.set_user(user.id, user.username, user.first_name, user.last_name)
    await message.answer('Подробную информацию о боте можно посмотреть по команде /info')
    await message.answer('Отправьте любое слово для перевода')


@router.message(Command('chatid'))
async def get_chat_id(message: Message):
    await message.answer(f"chat_id: {message.chat.id}")


@router.message(Command('info'))
async def get_info(message: Message):
    await message.answer('Чтобы начать пользоваться ботом, просто отправьте слово на русском или одном из дагестанских языков, и бот постарается найти перевод\n'
                         'Чтобы поменять язык (по умолчанию стоит лезгинский), используйте команду /lang\n\n'
                         'Для изменения режима перевода используйте команду /mode\n'
                         'простой режим: ищет слово целиком,\n'
                         'комплексный режим - ищет любые совпадения, в том числе во фразах\n\n'
                         'Чтобы добавить свой перевод, используйте команду /add, а затем следуйте инструкциям\n'
                         'По дополнительным вопросам: /help')


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Появились вопросы или идеи? Пиши: @translatedag')


@router.message(Command('lang'))
async def set_language(message: Message):
        await message.answer('Выберите язык для перевода', reply_markup=await kb.inline_languages())


@router.callback_query(F.data.startswith('lang_'))
async def language_handler(callback: CallbackQuery):
    lang: str = callback.data.replace('lang_', '')
    await callback.answer()
    user_id = callback.from_user.id
    try:
        await rq.set_language(user_id, lang)
        await settings_manager.update(user_id=user_id, lang=lang)
        await callback.message.edit_text(
            f'Вы выбрали {next((k for k, v in kb.languages.items() if v == lang), "Неизвестный")} язык'
        )

    except Exception as e:
        print(e)
        await callback.message.edit_text('Что-то пошло не так. /help')

@router.message(Command('mode'))
async def mode(message: Message):
    await message.answer('Выберите режим перевода', reply_markup=kb.modes)


@router.callback_query(F.data.startswith('mode_'))
async def mode_handler(callback: CallbackQuery):
    mode: str = callback.data.replace('mode_', '')
    await callback.answer()

    user_id = callback.from_user.id
    try:
        await rq.set_mode(user_id, mode)
        await settings_manager.update(user_id=user_id, mode=mode)
        if mode == "simple":
            await callback.message.edit_text('Вы выбрали простой режим перевода')
        else:
            await callback.message.edit_text('Вы выбрали комплексный режим перевода')
    except:
        await callback.message.edit_text('Что-то пошло не так. /help')


@router.message(Command('add'))
async def add(message: Message, state: FSMContext):
    from_user = message.from_user
    await rq.update_user_info(
        tg_id=from_user.id,
        username=from_user.username,
        first_name=from_user.first_name,
        last_name=from_user.last_name
    )

    await message.answer("Напишите слово на лезгинском, синонимы разделяйте точкой с запятой и пробелом (; )")
    await state.set_state(AddWordStates.word)


@router.message(AddWordStates.word)
async def process_word(message: Message, state: FSMContext):
    await state.update_data(word=message.text.strip())
    await message.answer('Теперь напишите перевод слова(ов) на русский, синонимы также через ; ')
    await state.set_state(AddWordStates.translation)


@router.message(AddWordStates.translation)
async def process_translation(message: Message, state: FSMContext):
    await state.update_data(translation=message.text.strip())
    await message.answer('Теперь приведите примеры употребления вместе с переводами'
                         ' (или напишите "-" если не нужно)')
    await state.set_state(AddWordStates.examples)


@router.message(AddWordStates.examples)
async def process_examples(message: Message, state: FSMContext):
    await state.update_data(examples=message.text.strip().replace('-', ''))
    await message.answer('Если хотите, добавьте заметки (или напишите "-" если не нужно)')
    await state.set_state(AddWordStates.notes)


@router.message(AddWordStates.notes)
async def process_notes(message: Message, state: FSMContext):
    user_data = await state.update_data(notes=message.text.strip().replace('-', ''))
    await state.clear()

    # Сохраняем в БД
    word = user_data['word']
    translation = user_data['translation']
    examples = user_data['examples']
    notes = user_data['notes']

    try:
        await rq.add_entry(word, translation, message.from_user.id,
                           examples if examples else '', notes if notes else '')
        await message.answer("Словарная статья успешно добавлена! ✅")
    except Exception as e:
        await message.answer(f"Произошла ошибка при сохранении: {e}")
