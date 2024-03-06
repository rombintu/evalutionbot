from aiogram import Bot
import os

from dotenv import load_dotenv
load_dotenv()

bot = Bot(os.getenv("TOKEN"), parse_mode=None, disable_web_page_preview=True)