import os

import img2pdf
from PIL import Image


def change_extension(filename, extension):
    file, _ = os.path.splitext(filename)
    return file + extension


def to_jpg(filename):
    outfile = change_extension(filename, ".jpg")
    if filename == outfile:
        return outfile

    fill_color = '#000000'
    image = Image.open(filename)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new(image.mode[:-1], image.size, fill_color)
        background.paste(image, image.split()[-1])
        image = background
    try:
        image.save(outfile)
        return outfile
    except IOError:
        print("cannot convert", filename)


def to_png(filename):
    outfile = change_extension(filename, ".png")
    if filename == outfile:
        return outfile

    image = Image.open(filename)
    try:
        image.save(outfile)
        return outfile
    except IOError:
        print("cannot convert", filename)


def to_pdf(filename):
    # library does not work with alpha channels
    filename = to_jpg(filename)
    outfile = change_extension(filename, ".pdf")
    if filename == outfile:
        return outfile

    with open(outfile, "wb") as f:
        f.write(img2pdf.convert(filename))
