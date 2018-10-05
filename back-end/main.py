import logging
import os
import traceback
from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

from fileops import convert

log = logging.getLogger("main")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["ALLOWED_EXTENSIONS"] = set(
    ["pdf", "png", "jpg", "jpeg", "jpg_large"]
)
app.config["SUPPORTED_CONVERSIONS"] = {
    "jpg": ["jpg", "pdf", "png"],
    "jpg_large": ["jpg", "pdf", "png"],
    "jpeg": ["jpg", "pdf", "png"],
    "pdf": ["pdf"],
    "png": ["jpg", "pdf", "png"],
}
app.config["CONVERT"] = {
    "jpg": convert.to_jpg,
    "pdf": convert.to_pdf,
    "png": convert.to_png,
}

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["UPLOAD_FOLDER_PATH"] = os.path.join(
    app.root_path, app.config["UPLOAD_FOLDER"]
)


def get_extension(filename):
    _, e = os.path.splitext(filename)
    return e.lower()[1:]


def check_extension(filename):
    ext = get_extension(filename)
    return ext in app.config["ALLOWED_EXTENSIONS"]


def allowed_file(filename):
    return "." in filename and check_extension(filename)


def check_supported_conversion(output, filename):
    input = get_extension(filename)
    if output not in app.config["SUPPORTED_CONVERSIONS"][input]:
        raise ValueError("Conversion not supported")


def log_error(e, inputfile):
    log.error("cannot convert {}, error: {}".format(inputfile.filename, e))
    log.error(traceback.format_exc())


def upload(inputfile):
    if not allowed_file(inputfile.filename):
        raise ValueError("File not supported")
    filename = secure_filename(inputfile.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER_PATH"], filename)
    log.info("Saving to {}".format(filepath))
    inputfile.save(filepath)
    return filepath


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 204
        inputfile = request.files["file"]

        if inputfile.filename == "":
            return "No selected file", 204

        try:
            log.info("About to upload {}".format(inputfile))
            inputfilepath = upload(inputfile)
            requested_conversion = request.form.get("output")
            check_supported_conversion(requested_conversion, inputfilepath)
            converter = app.config["CONVERT"][requested_conversion]
            outputfile = converter(inputfilepath)
        except ValueError as e:
            log_error(e, inputfile)
            return str(e), 400
        except Exception as e:
            log_error(e, inputfile)
            return str(e), 500
        return redirect(os.path.join(app.config["UPLOAD_FOLDER"], outputfile))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <select type="text" name="output">
            <option value="jpg">JPG</option>
            <option value="png">PNG</option>
            <option value="pdf" selected>PDF</option>
        </select>
        <input type="submit" value="Convert">
    </form>
    """


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER_PATH"], filename)


if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER_PATH"]):
        log.info("Creating {}".format(app.config["UPLOAD_FOLDER_PATH"]))
        path = app.config["UPLOAD_FOLDER_PATH"]
        os.makedirs(path)
        status = "Created" if os.path.exists(path) else "Did not create"
        log.info("{} {}".format(status, path))

    app.run(host="0.0.0.0", port=9000, debug=True)
