from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery    # CallbackQuery - События, при нажатии на кнопки
from aiogram.fsm.state import StatesGroup, State   # Состояние
from aiogram.fsm.context import FSMContext         # FSMContext - нужен для управления состояниями State

from datetime import timedelta

# Для кнопок
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton    # In msg


from config import Giga_authorization_key as SBER_AUTH, Giga_Scope

from gigachat import GigaChat

# inline keyboard для /help
help_commands = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='/start', callback_data='/start'),
     InlineKeyboardButton(text='/help', callback_data='/help')]
])

# Reply keyboard для /gen_py_code
start_codding = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = '/gen_py_code')]],
                                    # Подгоняем размер
                                    resize_keyboard=True,
                                    # Пишет серым текстом на поле для вводы текста
                                    input_field_placeholder='Выберите пункт меню.',
                                    # Скрытие кнопки после использования
                                    one_time_keyboard=True
                                    )

# Подключаем ИИ для генерации кода (и не только)
model = GigaChat(
   credentials=SBER_AUTH,
   scope=Giga_Scope,
   model="GigaChat",
   verify_ssl_certs=False
)

router = Router()

class ReqGiga(StatesGroup):
    text_req = State()

# Декоратор, является деспетчером, метод .message - означает, что он ждёт именно сообщения
@router.message(CommandStart())
async def cmd_start(message: Message):
    start_msg = f'Привет! \nТвой ID: {message.from_user.id} \nИмя: {message.from_user.first_name}' \
                f' \nFor more inf. use /help '
    await message.reply(start_msg,
                        reply_markup=start_codding)
    print(f'Bot was started by @{message.from_user.username} at'
            f' {(message.date + timedelta(hours=3)).strftime("%H:%M:%S %Y:%m:%d")}')


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это команда /help '
                         '\nСписок команд:', reply_markup=help_commands)

# callbacks for /help
@router.callback_query(F.data=='/start')
async def msg_start(callback: CallbackQuery):
    await callback.answer('Выбрана команда /start', show_alert=False)
    await cmd_start(callback.message)

@router.callback_query(F.data=='/help')
async def msg_help(callback: CallbackQuery):
    await callback.answer('Выбрана команда /help', show_alert=False)
    await callback.message.edit_text('Это команда /help '
                         '\nСписок команд:', reply_markup=help_commands)


# Общение с ИИ (GigaChat)
@router.message(Command('gen_py_code'))
async def gen_py_code_start(message: Message, state: FSMContext):
    await state.set_state(ReqGiga.text_req)
    await message.answer('Введите ваш запрос на генерацию кода')

@router.message(ReqGiga.text_req)
async def gen_py_code_text(message: Message, state: FSMContext):
    await state.update_data(text_req=message.text)
    data = await state.get_data()
    data = data['text_req']
    start_text = 'Сгенерируй только код с комментариями на Python не используя заголовков Markdown для следующей задачи:'
    response = model.chat(start_text + data)
    Giga_answer = response.choices[0].message.content
    await message.answer(Giga_answer)
    # Удаление состояния, если не прописать, то могут начать срабатывать хендлеры выше (на имя, телефон)
    await state.clear()


# Заглушка для прочих сообщений
@router.message()
async def echo(message: Message):
    await message.answer(f'{message.text}?')