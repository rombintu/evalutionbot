# from aiogram.types import InlineKeyboardButton as btn
# from aiogram.types import InlineKeyboardMarkup as ikm
from aiogram.utils.keyboard import InlineKeyboardBuilder as ikbuilder


# def btns_list_skills():
#     builder = ikbuilder()
#     for key, skill in skills.items():
#         builder.button(text=skill.get('str'), callback_data=f"skills_{key}_route")
#     builder.adjust(3, 3)
#     return builder.as_markup()