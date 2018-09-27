import logging
import os

import img2pdf
from PIL import Image

log = logging.getLogger("convert")


def change_extension(filename, extension):
    file, _ = os.path.splitext(filename)
    return file + extension


def get_filename(filepath):
    return os.path.basename(filepath)


def to_jpg(input):
    output = change_extension(input, ".jpg")
    if input == output:
        return output

    log.debug("Converting {} to {}".format(
             get_filename(input), get_filename(output)))

    fill_color = '#000000'
    image = Image.open(input)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new(image.mode[:-1], image.size, fill_color)
        background.paste(image, image.split()[-1])
        image = background
    try:
        image.save(output)
        return get_filename(output)
    except IOError as e:
        log.error("cannot convert {}, error: {}".format(
            get_filename(input), e))


def to_png(input):
    output = change_extension(input, ".png")
    if input == output:
        return output

    log.debug("Converting {} to {}".format(
             get_filename(input), get_filename(output)))

    image = Image.open(input)
    try:
        image.save(output)
        return get_filename(output)
    except IOError as e:
        log.error("cannot convert {}, error: {}".format(
            get_filename(input), e))


def to_pdf(input):
    # library does not work with alpha channels
    input = to_jpg(input)
    output = change_extension(input, ".pdf")
    if input == output:
        return output

    log.debug("Converting {} to {}".format(
             get_filename(input), get_filename(output)))
    try:
        with open(output, "wb") as f:
            f.write(img2pdf.convert(input))
    except Exception as e:
        log.error("well played")
    return get_filename(output)
