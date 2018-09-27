import os
from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename

import convert

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'jpg_large'])

CONVERT = {
    'jpg': convert.to_jpg,
    'pdf': convert.to_pdf,
    'png': convert.to_png
}

SUPPORTED_CONVERSIONS = {
    'jpg': ['jpg', 'pdf', 'png'],
    'pdf': ['pdf'],
    'png': ['jpg', 'pdf', 'png']
}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_extension(filename):
    _, e = os.path.splitext(filename)
    return e


def check_extension(filename):
    return get_extension(filename).lower()[1:] in ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and check_extension(filename)


def check_supported_conversion(output, file):
    input = get_extension(file)
    if output not in SUPPORTED_CONVERSIONS[input]:
        raise ValueError("Conversion not supported")


def upload(file):
    if not allowed_file(file.filename):
        raise ValueError("File not supported")
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
            input_filepath = upload(file)
            requested_conversion = request.form.get('output')
            check_supported_conversion(requested_conversion, input_filepath)
            output_file = CONVERT[requested_conversion](input_filepath)
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            return str(e), 500

        return redirect(output_file)
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
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
