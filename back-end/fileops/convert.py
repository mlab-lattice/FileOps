import logging
import os

import img2pdf
from PIL import Image

log = logging.getLogger("convert")


def change_extension(filename, extension):
    basename, _ = os.path.splitext(filename)
    return basename + extension


def get_filename(filepath):
    return os.path.basename(filepath)


def to_jpg(inputfile):
    outputfile = change_extension(inputfile, ".jpg")
    if inputfile == outputfile:
        return get_filename(outputfile)

    log.info("Converting {} to {}".format(
        get_filename(inputfile), get_filename(outputfile))
    )

    fill_color = '#000000'
    image = Image.open(inputfile)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new(image.mode[:-1], image.size, fill_color)
        background.paste(image, image.split()[-1])
        image = background
    image.save(outputfile)
    return get_filename(outputfile)


def to_png(inputfile):
    outputfile = change_extension(inputfile, ".png")
    if inputfile == outputfile:
        return get_filename(outputfile)

    log.info("Converting {} to {}".format(
        get_filename(inputfile), get_filename(outputfile))
    )

    image = Image.open(inputfile)
    image.save(outputfile)
    return get_filename(outputfile)


def to_pdf(inputfile):
    outputfile = change_extension(inputfile, ".pdf")
    if inputfile == outputfile:
        return get_filename(outputfile)
    # library does not work with alpha channels, convert to jpg first
    jpg_input = to_jpg(inputfile)
    inputfile = change_extension(inputfile, ".jpg")

    log.info("Removed alpha channels for {}".format(jpg_input))

    log.info("Converting {} to {}".format(
        get_filename(inputfile), get_filename(outputfile))
    )
    with open(outputfile, "wb") as f:
        f.write(img2pdf.convert(inputfile))
    return get_filename(outputfile)
