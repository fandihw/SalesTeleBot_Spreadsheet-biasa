from telegram import Update
from telegram.ext import ContextTypes
import os
from services.drive import upload_photo
from services.spreadsheet import save_data
from datetime import datetime, timedelta, timezone  


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Ambil foto terakhir yg dikirim user
    photo_file = await update.message.photo[-1].get_file()

    # Simpan sementara ke lokal
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    # Upload ke Google Drive dan ambil URL
    drive_url = upload_photo(file_path)

    # Ambil data sebelumnya dari user_data dan tambahkan info baru
    data = context.user_data.copy()
    data["photo_url"] = drive_url

    # Tambahkan timestamp zona WIB
    wib = timezone(timedelta(hours=7))
    data["timestamp"] = datetime.now(wib)

    # Simpan ke Google Spreadsheet (otomatis ke Visit Baru atau Follow Up)
    save_data(data)

    await update.message.reply_text("✅ Data dan eviden berhasil dikirim. Terima kasih!")
