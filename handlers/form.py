import os
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from services.spreadsheet import save_data
from services.drive import upload_photo

# ────────────── Konstanta dan Konfigurasi ──────────────
WIB = timezone(timedelta(hours=7))

TELDA_STO_MAP = {
    "Bangkalan": ["SPG", "KML", "ARB", "KPP", "BKL", "OMB", "BEA", "TBU"],
    "Gresik": ["CRM", "POG", "BPG", "DDS", "SDY", "KDE", "BWN", "GSK"],
    "Lamongan": ["SDD", "LMG", "BBA", "BDG"],
    "Pamekasan": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Tandes": ["DMO", "TNS", "KNN", "BBE", "KLN", "LKI", "KRP"],
    "Ketintang": ["WRU", "IJK", "RKT", "TPO"],
    "Manyar": ["GBG", "MYR", "JGR", "MGO"],
    "Kanjeran": ["KPS", "PRK", "KBL", "KJR"],
}

STEPS = [
    "kategori", "nama_sales", "telda", "sto", "kegiatan", "poi_name", "address",
    "ekosistem", "contact_name", "contact_position", "contact_phone",
    "provider", "provider_detail", "cost", "feedback", "feedback_detail",
    "detail_info"
]

OPTIONS = {
    "kategori": ["Visit Baru", "Follow Up"],
    "telda": list(TELDA_STO_MAP.keys()),
    "kegiatan": ["Door to Door", "Out Bond Call"],
    "ekosistem": [
        "Ruko", "Sekolah", "Hotel", "Multifinance", "Health", "Ekspedisi",
        "Energi", "Agriculture", "Properti", "Manufaktur", "Media & Communication"
    ],
    "provider": ["Telkom Group", "Kompetitor", "Belum Berlangganan Internet"],
    "provider_detail_telkom": ["Indihome", "Indibiz", "Wifi.id", "Astinet", "Other"],
    "provider_detail_kompetitor": [
        "MyRep", "Biznet", "FirtsMedia", "Iconnet", "XL Smart",
        "Indosat MNCPlay", "IFORTE", "Hypernet", "CBN", "Fibernet", "Fiberstar", "Other"
    ],
    "feedback": [
        "Bertemu dengan PIC/Owner/Manajemen", "Tidak bertemu dengan PIC"
    ],
    "feedback_detail_ya": [
        "Tertarik Berlangganan Indibiz", "Tidak Tertarik Berlangganan Indibiz",
        "Ragu-ragu atau masih dipertimbangkan"
    ],
    "feedback_detail_tidak": [
        "Mendapatkan Kontak Owner/PIC/Manajemen", "Tidak Mendapatkan Kontak Owner/PIC/Manajemen"
    ],
}

LABELS = {
    "kategori": "Kategori",
    "nama_sales": "Nama Sales",
    "telda": "Telda",
    "sto": "STO",
    "poi_name": "Nama POI",
    "address": "Alamat",
    "ekosistem": "Ekosistem",
    "kegiatan": "Jenis Kegiatan",
    "contact_name": "Nama PIC",
    "contact_position": "Jabatan PIC",
    "contact_phone": "HP",
    "provider": "Provider",
    "provider_detail": "Jenis Provider",
    "cost": "Abonemen",
    "feedback": "Feedback",
    "feedback_detail": "Detail Feedback",
    "detail_info": "Info Tambahan",
}

# ────────────── START COMMAND ──────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("START", callback_data="start_clicked")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Silakan tekan tombol di bawah ini untuk memulai.", reply_markup=reply_markup)

async def start_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "👋🏻Selamat datang di *Sales Visit Bot*\n\n"
        "Gunakan /start untuk input baru",
        parse_mode=ParseMode.MARKDOWN_V2
    )

# ────────────── Handler Callback ──────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = query.data

    if selected == "start_clicked":
        await start_clicked(update, context)
        return

    if selected in ["confirm_data", "cancel_data"]:
        await handle_confirmation(update, context)
        return

    step = context.user_data.get("step")
    context.user_data[step] = selected
    await query.edit_message_text(f"✅ Anda memilih: *{escape_markdown(selected, version=2)}*", parse_mode=ParseMode.MARKDOWN_V2)

    if step == "telda":
        context.user_data["step"] = "sto"
        keyboard = [[InlineKeyboardButton(sto, callback_data=sto)] for sto in TELDA_STO_MAP[selected]]
        await query.message.reply_text(f"Anda memilih {selected}, pilih STO:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if step == "provider":
        if selected == "Belum Berlangganan Internet":
            context.user_data.update({"provider_detail": "-", "cost": "-", "step": "feedback"})
            await query.message.reply_text("ℹ️ Provider & abonemen dilewati.")
            await ask_next(update, context)
            return
        context.user_data["step"] = "provider_detail"
        dkey = "provider_detail_telkom" if selected == "Telkom Group" else "provider_detail_kompetitor"
        keyboard = [[InlineKeyboardButton(x, callback_data=x)] for x in OPTIONS[dkey]]
        await query.message.reply_text("Pilih jenis provider:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if step == "provider_detail" and selected == "Other":
        await query.message.reply_text("Masukkan nama provider lainnya:")
        return

    if step == "feedback":
        context.user_data["step"] = "feedback_detail"
        dkey = "feedback_detail_ya" if selected.startswith("Bertemu") else "feedback_detail_tidak"
        keyboard = [[InlineKeyboardButton(x, callback_data=x)] for x in OPTIONS[dkey]]
        await query.message.reply_text("Pilih detail feedback:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    next_idx = STEPS.index(step) + 1
    if next_idx < len(STEPS):
        context.user_data["step"] = STEPS[next_idx]
        await ask_next(update, context)
    else:
        await query.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")

# ────────────── Handler Input Text ──────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step not in STEPS:
        await update.message.reply_text("Terjadi kesalahan. /start untuk ulang.")
        return

    context.user_data[step] = update.message.text
    await update.message.reply_text(f"✅ Anda mengisi: *{escape_markdown(update.message.text, version=2)}*", parse_mode=ParseMode.MARKDOWN_V2)

    next_idx = STEPS.index(step) + 1
    if next_idx < len(STEPS):
        context.user_data["step"] = STEPS[next_idx]
        await ask_next(update, context)
    else:
        await update.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")

# ────────────── Pertanyaan Langkah Berikutnya ──────────────
async def ask_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    label = LABELS.get(step, step)
    msg = update.effective_message

    if step in OPTIONS:
        keyboard = [[InlineKeyboardButton(val, callback_data=val)] for val in OPTIONS[step]]
        await msg.reply_text(f"Pilih {label}:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(f"Masukkan {label}:")

# ────────────── Handler Upload Foto ──────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()

    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    photo_url = upload_photo(file_path)

    form_data = context.user_data.copy()
    form_data.update({
        "photo_url": photo_url,
        "timestamp": datetime.now(WIB),
        "user_id": str(user_id)
    })
    context.user_data["form_data"] = form_data

    await show_confirmation(update, context)

# ────────────── Konfirmasi Akhir ──────────────
async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    form_data = context.user_data.get("form_data", {})
    lines = ["📋 Berikut ringkasan data yang Anda input:"]
    for key in STEPS:
        label = LABELS.get(key, key)
        value = form_data.get(key, "-")
        lines.append(f"*{escape_markdown(label, version=2)}*: {escape_markdown(str(value), version=2)}")

    keyboard = [[
        InlineKeyboardButton("✅ Konfirmasi", callback_data="confirm_data"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_data")
    ]]

    await update.effective_message.reply_text(
        "\n".join(lines) +
        "\n\n❗❗*PASTIKAN DATA YANG ANDA INPUTKAN SUDAH BENAR*❗❗\n" +
        "• Klik ✅ *Konfirmasi* kalau sudah benar\n" +
        "• Klik ❌ *Cancel* untuk mengulang dari awal",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ────────────── Simpan Data atau Batalkan ──────────────
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_data":
        data = context.user_data.get("form_data")
        if data:
            msg = save_data(data)
            context.user_data.clear()
            await query.edit_message_text(msg)
            await query.message.reply_text(
                "👋 Selamat datang di *Sales Visit Bot*\n\n"
                "Gunakan /start untuk input baru\n"
                "Gunakan /cekdata untuk lihat 30 data terakhir",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await query.edit_message_text("❗ Data tidak ditemukan. Silakan ulangi")

    elif query.data == "cancel_data":
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Input dibatalkan. Silakan mulai ulang dengan /start",
            parse_mode=ParseMode.MARKDOWN_V2
        )