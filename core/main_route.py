import os
from aiogram import Dispatcher, types, F
from aiogram.filters.command import Command
# from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from core.routes.converting import Form
from core.content import *
from core.keyboards import *
from core.routes import converting
from tools.utils import logger
from tools.bot import bot
from dotenv import load_dotenv
load_dotenv()

# bot = Bot(os.getenv("TOKEN"), parse_mode=None, disable_web_page_preview=True)
dp = Dispatcher()
dp.include_router(converting.router)

async def setup_bot_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Активация бота, помощь"),
        types.BotCommand(command="/convert", description="Смарт конвертация файлов")
    ]
    await bot.set_my_commands(bot_commands)

async def start_bot():
    logger.info("Bot is starting...")
    await setup_bot_commands()
    await dp.start_polling(bot)

@dp.message(Command('start', 'activate'))
async def handle_message_start(message: types.Message):
    await message.answer(
        start_message,
        parse_mode="markdown",
    )

@dp.message(Command('convert'))
async def handle_command_converting(message: types.Message, state: FSMContext):
    await state.set_state(Form.input_file)
    await message.answer("Скинь документ или фото, посмотрим что с ним можно сделать\n/cancel - Отмена")
