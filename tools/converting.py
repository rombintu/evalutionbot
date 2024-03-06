from shell import shell
import os
from tools.utils import logger
from fpdf import FPDF
def check_exists_file(file_path):
    return os.path.isfile(file_path) and os.path.exists(file_path)

def doc2any(input_file_path, tmp_dir, output_file_path, output_type='pdf'):
    if not check_exists_file(input_file_path):
        return f"File {input_file_path} - not found"
    cmd = f"libreoffice --headless --convert-to '{output_type}' {input_file_path} --outdir {tmp_dir}"
    data = shell(cmd)
    logger.debug(cmd)
    logger.debug(f"Proccess converting: {data.output()}")
    logger.warning(f"Errors: {data.errors()}")

    if not check_exists_file(output_file_path):
        return f"File {output_file_path} - not found"
    return None

def jpg2pdf(images_paths: list, output_file_path: str):
    pdf = FPDF()
    for image in images_paths:
        pdf.add_page()
        pdf.image(image, x=10, y=10, w=175)
    pdf.output(output_file_path, "F")
    if not check_exists_file(output_file_path):
        return f"File {output_file_path} - not found"
    return None
