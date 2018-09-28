import logging
import os
from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

import convert

log = logging.getLogger("main")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = set(
    ['pdf', 'png', 'jpg', 'jpeg', 'jpg_large'])
app.config['SUPPORTED_CONVERSIONS'] = {
    'jpg': ['jpg', 'pdf', 'png'],
    'jpg_large': ['jpg', 'pdf', 'png'],
    'jpeg': ['jpg', 'pdf', 'png'],
    'pdf': ['pdf'],
    'png': ['jpg', 'pdf', 'png']
}
app.config['CONVERT'] = {
    'jpg': convert.to_jpg,
    'pdf': convert.to_pdf,
    'png': convert.to_png
}

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['UPLOAD_FOLDER_PATH'] = os.path.join(
    app.root_path, app.config['UPLOAD_FOLDER'])


def get_extension(filename):
    _, e = os.path.splitext(filename)
    return e.lower()[1:]


def check_extension(filename):
    ext = get_extension(filename)
    return ext in app.config['ALLOWED_EXTENSIONS']


def allowed_file(filename):
    return '.' in filename and check_extension(filename)


def check_supported_conversion(output, file):
    input = get_extension(file)
    if output not in app.config['SUPPORTED_CONVERSIONS'][input]:
        raise ValueError("Conversion not supported")


def upload(file):
    if not allowed_file(file.filename):
        raise ValueError("File not supported")
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER_PATH'], filename)
    log.info("Saving to {}".format(filepath))
    file.save(filepath)
    return filepath


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 204
        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 204

        try:
            log.info("About to upload {}".format(file))
            input_filepath = upload(file)
            requested_conversion = request.form.get('output')
            check_supported_conversion(requested_conversion, input_filepath)
            converter = app.config['CONVERT'][requested_conversion]
            output_file = converter(input_filepath)
        except ValueError as e:
            log.error(e)
            return str(e), 400
        except Exception as e:
            log.error(e)
            return str(e), 500
        return redirect(os.path.join(app.config['UPLOAD_FOLDER'], output_file))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <select type=text name="output">
            <option value="jpg">JPG</option>
            <option value="png">PNG</option>
            <option value="pdf" selected>PDF</option>
        </select>
        <input type=submit value=Convert>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_PATH'],
                               filename)


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER_PATH']):
        log.info("Creating {}".format(app.config['UPLOAD_FOLDER_PATH']))
        os.makedirs(app.config['UPLOAD_FOLDER_PATH'])
        log.info("{} {}".format(
            "Created"
            if os.path.exists(app.config['UPLOAD_FOLDER_PATH'])
            else "Did not create",
            app.config['UPLOAD_FOLDER_PATH'])
        )

    app.run(host="0.0.0.0", port=9000, debug=True)
