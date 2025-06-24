import os
import subprocess
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)


# Настройки
TOKEN = "7620213058:AAFx_XbadXg3l4xzvC5LsBAuWtyxdqBy3t0"  
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_EBOOK_EXTENSIONS = {"epub", "mobi", "azw3", "pdf", "txt", "fb2", "docx"}
CHOOSE_FORMAT = 1


# Функции конвертации из app
def convert_image(old_path, new_path, new_extension):
    with Image.open(old_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if new_extension.lower() == "pdf":
            img.save(new_path, "PDF")
        else:
            img.save(new_path)

def convert_ebook(old_path, new_path):
    calibre_path = r"C:\Program Files\Calibre2\ebook-convert.exe"  # Укажи свой путь
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
    while os.path.exists(os.path.join(UPLOAD_FOLDER, new_filename)):
        new_filename = f"{name}_{counter}.{new_extension}"
        counter += 1
    return new_filename


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-конвертер. Отправь мне изображение (jpg, jpeg, png) или электронную книгу (epub, mobi, azw3, pdf, txt, fb2, docx)."
    )
    return ConversationHandler.END

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file:
        await update.message.reply_text("Пожалуйста, отправь файл!")
        return ConversationHandler.END


    # Сохраняем файл
    file_name = file.file_name
    extension = file_name.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_EBOOK_EXTENSIONS):
        await update.message.reply_text("Неподдерживаемый формат файла!")
        return ConversationHandler.END

    old_path = os.path.join(UPLOAD_FOLDER, file_name)
    telegram_file = await file.get_file()
    await telegram_file.download_to_drive(old_path)

    # Сохраняем путь 
    context.user_data["old_path"] = old_path
    context.user_data["old_filename"] = file_name
    context.user_data["extension"] = extension

    # Создаём варианты форматов
    keyboard = []
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        formats = ALLOWED_IMAGE_EXTENSIONS.union({"pdf"}) - {extension}
        for fmt in sorted(formats):
            keyboard.append([InlineKeyboardButton(fmt.upper(), callback_data=fmt)])
    elif extension in ALLOWED_EBOOK_EXTENSIONS:
        formats = ALLOWED_EBOOK_EXTENSIONS - {extension}
        for fmt in sorted(formats):
            keyboard.append([InlineKeyboardButton(fmt.upper(), callback_data=fmt)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери формат для конвертации:", reply_markup=reply_markup)
    return CHOOSE_FORMAT

async def choose_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    new_extension = query.data.lower()
    old_path = context.user_data["old_path"]
    old_filename = context.user_data["old_filename"]
    extension = context.user_data["extension"]

    new_filename = rename_file(old_filename, new_extension)
    new_path = os.path.join(UPLOAD_FOLDER, new_filename)

    try:
        if extension in ALLOWED_IMAGE_EXTENSIONS and new_extension in ALLOWED_IMAGE_EXTENSIONS.union({"pdf"}):
            convert_image(old_path, new_path, new_extension)
        elif extension in ALLOWED_EBOOK_EXTENSIONS and new_extension in ALLOWED_EBOOK_EXTENSIONS:
            convert_ebook(old_path, new_path)
        else:
            await query.message.reply_text("Неподдерживаемая комбинация форматов!")
            os.remove(old_path)
            return ConversationHandler.END

        # Отправляем сконвертированный файл
        with open(new_path, "rb") as f:
            await query.message.reply_document(f, filename=new_filename)

        # Очистка файлов
        os.remove(old_path)
        os.remove(new_path)
        await query.message.reply_text("Конвертация завершена! Отправь новый файл для конвертации.")
    except Exception as e:
        await query.message.reply_text(f"Ошибка конвертации: {e}")
        if os.path.exists(old_path):
            os.remove(old_path)
        if os.path.exists(new_path):
            os.remove(new_path)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    if "old_path" in context.user_data and os.path.exists(context.user_data["old_path"]):
        os.remove(context.user_data["old_path"])
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Document.ALL, handle_file)],
        states={
            CHOOSE_FORMAT: [CallbackQueryHandler(choose_format)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()