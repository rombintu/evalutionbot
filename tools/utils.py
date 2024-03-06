from loguru import logger
import os

def delete_file(files):
    for file in files:
        try:
            os.remove(file)
        except FileExistsError as err:
            logger.error(err)

def search_files_from_name(dir, file_name):
    found_files = []
    for r, _, f in os.walk(dir):
        for file in f:
            if file.startswith(f"{file_name}.") or file.endswith(f".jpg"):
                found_files.append(os.path.join(r, file))
    return found_files