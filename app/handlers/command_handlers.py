from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
import database.requests as rq

router = Router()

class AddWordStates(StatesGroup):
    word = State()
    translation = State()
    examples = State()
    notes = State()


@router.message(CommandStart())
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Подробную информацию о боте можно посмотреть по команде /info')
    await message.answer('Отправьте любое слово для перевода')


@router.message(Command('chatid'))
async def get_chat_id(message: Message):
    await message.answer(f"chat_id: {message.chat.id}")


@router.message(Command('help'))
async def help(message: Message):
    await message.answer('По техническим вопросам: @RipeR3d')


@router.message(Command('mode'))
async def mode(message: Message):
    await message.answer('Выберите режим перевода', reply_markup=kb.modes)


@router.callback_query(F.data.startswith('mode_'))
async def mode_handler(callback: CallbackQuery):
    mode: str = callback.data.replace('mode_', '')
    await callback.answer()
    try:
        await rq.set_mode(callback.message.chat.id, mode)
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
