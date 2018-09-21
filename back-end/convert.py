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
        return get_filename(output)

    log.info("Converting {} to {}".format(
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
        return get_filename(output)

    log.info("Converting {} to {}".format(
             get_filename(input), get_filename(output)))

    image = Image.open(input)
    try:
        image.save(output)
        return get_filename(output)
    except IOError as e:
        log.error("cannot convert {}, error: {}".format(
            get_filename(input), e))


def to_pdf(input):
    output = change_extension(input, ".pdf")
    if input == output:
        return get_filename(output)
    # library does not work with alpha channels, convert to jpg first
    input = change_extension(input, ".jpg")
    jpg_input = to_jpg(input)
    log.info("Removed alpha channels for {}".format(jpg_input))

    log.info("Converting {} to {}".format(
             get_filename(input), get_filename(output)))
    try:
        with open(output, "wb") as f:
            f.write(img2pdf.convert(input))
    except Exception as e:
        log.error(e)
    return get_filename(output)
