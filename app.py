from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_EBOOK_EXTENSIONS = {'epub', 'mobi', 'azw3', 'pdf', 'txt', 'fb2', 'docx'}

def convert_image(old_path, new_path, new_extension):
    with Image.open(old_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if new_extension.lower() == 'pdf':
            img.save(new_path, "PDF")
        else:
            img.save(new_path)

def convert_ebook(old_path, new_path):
    calibre_path = r"C:\Program Files\Calibre2\ebook-convert.exe"  # или путь, который у тебя
    try:
        subprocess.run([calibre_path, old_path, new_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Ошибка при конвертации книги: " + str(e))
    except FileNotFoundError as e:
        raise RuntimeError("Утилита ebook-convert не найдена. Проверь путь.")


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
        extension = old_filename.rsplit('.', 1)[-1].lower()
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
        file.save(old_path)

        new_extension = request.form.get('new_extension').lower()
        new_filename = rename_file(old_filename, new_extension)
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

        try:
            if extension in ALLOWED_IMAGE_EXTENSIONS and new_extension in ALLOWED_IMAGE_EXTENSIONS.union({'pdf'}):
                convert_image(old_path, new_path, new_extension)
            elif extension in ALLOWED_EBOOK_EXTENSIONS and new_extension in ALLOWED_EBOOK_EXTENSIONS:
                convert_ebook(old_path, new_path)
            else:
                raise ValueError("Неподдерживаемая комбинация форматов.")
            os.remove(old_path)
        except Exception as e:
            print(f"Ошибка: {e}")
            return f"Ошибка конвертации: {e}", 500

        return send_from_directory(app.config['UPLOAD_FOLDER'], new_filename, as_attachment=True)

    return "Invalid file", 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
