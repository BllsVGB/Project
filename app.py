from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def convert_file(old_path, new_path, new_extension):
    new_extension = new_extension.lower()
    with Image.open(old_path) as img:
        # Автоматическое преобразование в RGB, если нужно
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if new_extension in ["jpg", "jpeg", "png"]:
            img.save(new_path)
        elif new_extension == "pdf":
            img.save(new_path, "PDF")
        else:
            raise ValueError("Unsupported format")


def rename_file(old_filename, new_extension):
    name, _ = os.path.splitext(old_filename)
    new_filename = f"{name}.{new_extension}"
    counter = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)):
        new_filename = f"{name}_{counter}.{new_extension}"
        counter += 1
    return new_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        old_filename = file.filename
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
        file.save(old_path)

        new_extension = request.form.get('new_extension')
        new_filename = rename_file(old_filename, new_extension)
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

        try:
            convert_file(old_path, new_path, new_extension)
            os.remove(old_path)
        except Exception as e:
            print(f"Error: {e}")
            return "Conversion failed. Make sure the format is supported.", 500

        return send_from_directory(app.config['UPLOAD_FOLDER'], new_filename, as_attachment=True)

    return "Invalid file", 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
