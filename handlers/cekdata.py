from telegram import Update
from telegram.ext import ContextTypes
from services.spreadsheet import get_last_30_days_data
from services import is_user_allowed, is_admin
from datetime import timezone, timedelta
from html import escape

# Fungsi bantu untuk padding label
def fmt(label, value):
    return f"{label:<22}: {escape(str(value) if value else '-')}"

# Format pesan tiap entry
def format_data(entry):
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        "<pre>\n"
        "📌 Data Kunjungan Sales\n"
        f"{fmt('🗓️ Tanggal/Waktu', time_str)}\n"
        f"{fmt('📁 Kategori', entry.get('Kategori'))}\n"
        f"{fmt('👤 Nama Sales', entry.get('Nama Sales'))}\n"
        f"{fmt('🌏 Wilayah Telda', entry.get('Telda'))}\n"
        f"{fmt('🏬 STO', entry.get('STO'))}\n"
        f"{fmt('🎯 Jenis Kegiatan', entry.get('Kegiatan'))}\n"
        "\n"
        f"{fmt('🏢 Nama POI', entry.get('POI Name'))}\n"
        f"{fmt('📍 Alamat', entry.get('Alamat'))}\n"
        f"{fmt('🌐 Ekosistem', entry.get('Ekosistem'))}\n"
        "\n"
        f"{fmt('👥 Nama PIC', entry.get('Nama PIC'))}\n"
        f"{fmt('🧑‍💼 Jabatan PIC', entry.get('Jabatan PIC'))}\n"
        f"{fmt('📞 No.hp PIC', entry.get('HP'))}\n"
        "\n"
        f"{fmt('💡 Provider', entry.get('Provider'))}\n"
        f"{fmt('🔌 Nama Provider', entry.get('Provider Detail'))}\n"
        f"{fmt('💰 Abonemen Berlangganan', entry.get('Abonemen'))}\n"
        "\n"
        f"{fmt('💬 Feedback', entry.get('Feedback'))}\n\n"              
        f"{fmt('💬 Detail Feedback', entry.get('Feedback Detail'))}\n\n"
        f"{fmt('📝 Info Tambahan', entry.get('Info Tambahan'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "</pre>"
    )

# Handler /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ Anda tidak memiliki izin untuk melihat data ini")
        return

    entries = get_last_30_days_data()
    if not entries:
        await update.message.reply_text("📭 Tidak ada data dalam 30 hari terakhir")
        return

    # Filter data untuk user biasa
    if not is_admin(user_id):
        entries = [e for e in entries if str(e.get("User ID")) == str(user_id)]

    if not entries:
        await update.message.reply_text("📭 Tidak ada data kunjungan milik Anda dalam 30 hari terakhir")
        return

    # Kirim maksimal 30 entry
    for i, entry in enumerate(entries[:30], start=1):
        msg = format_data(entry)
        await update.message.reply_text(msg, parse_mode="HTML")