from aiogram.utils.keyboard import InlineKeyboardBuilder as ikbuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder as rkbuilder
from aiogram.types import InlineKeyboardButton as btn
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.types import FSInputFile
from tools.converting import doc2any, jpg2pdf
from tools.utils import logger, delete_file, search_files_from_name
import os


router = Router()

route_name = "converting"
help_message = "Скинь мне файл формата"
function_not_working = "Функция не работает"
tmp_dir = os.path.join(os.getcwd(), "tmp")


word_type = 'doc'
word_type_x = 'docx'
word_type_os = 'odt'
image_type = "jpg"

document_types = {
    word_type: ['pdf', 'epub', 'html', 'txt'],
    word_type_x: ['pdf', 'epub', 'html', 'txt'],
    word_type_os: ['pdf', 'epub', 'html', 'txt'],
    image_type: ['pdf']
}

pretty_document_type = {
    "pdf": "pdf",
    "epub": "epub",
    "html": "html:XHTML Writer File:UTF8",
    "txt": "txt:Text (encoded):UTF8",
}

user_delivery_photo: dict = {}

class Form(StatesGroup):
    input_file = State()

def btns_done():
    builder = rkbuilder()
    builder.button(text="Готово")
    return builder.as_markup()

def btns_delete(file_id):
    builder = ikbuilder()
    builder.button(text="Удалить все файлы", callback_data=f"{route_name}_{file_id}_delete")
    return builder.as_markup()

def btns_list_types(file_id: str, from_type: str):
    builder = ikbuilder()
    for to_type in document_types.get(from_type):
        # logger.debug(f"{route_name}_{file_id}_{from_type}_{to_type}")
        builder.button(text=to_type, callback_data=f"{route_name}_{file_id}_{from_type}_{to_type}")
    builder.adjust(1, 1)
    builder.row(btn(text="Удалить все файлы", callback_data=f"{route_name}_{file_id}_delete"))
    return builder.as_markup()

async def handle_error(message: types.Message, err="Произошла ошибка"):
    await message.answer(err) 

async def handle_waiting(message: types.Message):
    await message.answer("Обработка...")    

async def get_file_meta_from_message(message: types.Message, want="document"):
    file_id = None
    file_type = None
    match want:
        case "document":
            file_id = message.document.file_id
            try:
                file_type = message.document.file_name.split(".")[-1]
            except ValueError as err:
                logger.error(err)
                await handle_error(message, "Ошибка, не могу определить тип файла")
                return
        case "photo":
            file_id = message.photo[-1].file_id
            file_type = "jpg"
    file = await message.bot.get_file(file_id)
    input_file_abs_path = os.path.join(tmp_dir, f"{file.file_unique_id}.{file_type}")
    await message.bot.download_file(file_path=file.file_path, destination=input_file_abs_path)
    return {
        "cloud_path": file.file_path,
        "filesystem_path": input_file_abs_path,
        "name": file.file_unique_id,
        "type": file_type
    }

@router.message(Form.input_file)
async def handle_converting(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await message.answer("Отмена ожидания")
        await state.clear()
        return
    if message.document:
        file_meta = await get_file_meta_from_message(message, want="document")
        if not file_meta:
            return
        match file_meta['type']:
            case "doc" | "docx":
                await message.answer("Выбери тип файла который хочешь получить", reply_markup=btns_list_types(file_meta['name'], file_meta['type']))
            case _:
                await handle_error(message, "Я не обучен использовать данный формат документа")
                return
    elif message.photo:
        file_meta = await get_file_meta_from_message(message, want="photo")
        if not file_meta:
            return
        await message.answer("Могу сделать из этого PDF, если хочешь, отправь еще фотографий", reply_markup=btns_done())
        if not user_delivery_photo.get(message.chat.id):
            user_delivery_photo[message.chat.id] = {"photos": []}
        user_delivery_photo[message.chat.id]['photos'].append(file_meta)
        await state.set_state(Form.input_file)
        return
    elif message.text.lower() == "готово":
        if user_delivery_photo.get(message.chat.id) and user_delivery_photo.get(message.chat.id).get('photos'):
            logger.debug(user_delivery_photo[message.chat.id])
            images_paths = []
            for photo_meta in tuple(user_delivery_photo[message.chat.id].get('photos')):
                await message.bot.download_file(file_path=photo_meta['cloud_path'], destination=photo_meta['filesystem_path'])
                images_paths.append(photo_meta['filesystem_path'])
            output_file_abs_path = os.path.join(tmp_dir, f"{message.chat.id}.pdf")
            err = jpg2pdf(images_paths, output_file_path=output_file_abs_path)
            delete_file(images_paths)
            if err:
                await message.answer(err)
            else:
                await message.bot.send_document(
                    message.chat.id, 
                    FSInputFile(output_file_abs_path),
                    reply_markup=btns_delete(str(message.chat.id)))
                await message.answer("Выполнено", reply_markup=types.reply_keyboard_remove.ReplyKeyboardRemove())
        user_delivery_photo[message.chat.id] = []
    elif message.text:
        await message.answer("Ожидается документ или фото\n/cancel - Отмена")
        return
    await state.clear()

@router.callback_query(F.data.startswith(f"{route_name}_"))
async def callbacks(c: types.CallbackQuery):
    data = c.data.split("_")[1:]
    match data:
        case [_, "delete"]:
            file_id_or_name = data[0]
            files_mark_as_deleted = search_files_from_name(tmp_dir, file_id_or_name)
            delete_file(files_mark_as_deleted)
            await c.answer("Файлы успешно удалены из файловой системы сервера")
            await c.message.delete()
        case [_, _, _]:
            file_id_or_name = data[0]
            from_type = data[1]
            to_type = data[2]
            to_type_pretty = pretty_document_type.get(data[2])
            output_file_abs_path = os.path.join(tmp_dir, f"{file_id_or_name}.{to_type}")
            input_file_abs_path = os.path.join(tmp_dir, f"{file_id_or_name}.{from_type}")
            error = doc2any(input_file_abs_path, tmp_dir, output_file_abs_path, to_type_pretty)
            if not error:
                send_file = FSInputFile(output_file_abs_path)
                await c.message.bot.send_document(c.message.chat.id, send_file)
                await c.answer("Файл готов")
            else:
                await c.answer(error)

        case _:
            await c.answer('Ошибка')
    await c.answer()