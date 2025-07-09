from telegram import Update
from telegram.ext import ContextTypes
from services.spreadsheet import get_last_30_days_data 
from datetime import timezone, timedelta
from html import escape

# Fungsi bantu untuk padding label
def fmt(label, value):
    return f"{label:<22}: {escape(str(value) if value else '-')}"

# Fungsi format data
def format_data(entry):
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        "<pre>\n"
        "📌 Data Kunjungan Sales\n"
        f"{fmt('🗓️ Tanggal/Waktu', time_str)}\n"
        f"{fmt('📁 Kategori', entry.get('kategori'))}\n"
        f"{fmt('👤 Nama Sales', entry.get('kkontak'))}\n"
        f"{fmt('🌏 Wilayah Telda', entry.get('telda'))}\n"
        f"{fmt('🏬 STO', entry.get('sto'))}\n"
        f"{fmt('🎯 Jenis Kegiatan', entry.get('kegiatan'))}\n"
        "\n"
        f"{fmt('🏢 Nama POI', entry.get('poi_name'))}\n"
        f"{fmt('📍 Alamat', entry.get('address'))}\n"
        f"{fmt('🌐 Ekosistem', entry.get('ekosistem'))}\n"
        "\n"
        f"{fmt('👥 Nama PIC', entry.get('contact_name'))}\n"
        f"{fmt('🧑‍💼 Jabatan PIC', entry.get('contact_position'))}\n"
        f"{fmt('📞 No.hp PIC', entry.get('contact_phone'))}\n"
        "\n"
        f"{fmt('💡 Provider', entry.get('provider'))}\n"
        f"{fmt('🔌 Nama Provider', entry.get('provider_detail'))}\n"
        f"{fmt('💰 Abonemen Berlangganan', entry.get('cost'))}\n"
        "\n"
        f"{fmt('💬 Feedback', entry.get('feedback'))}\n\n"              
        f"{fmt('💬 Detail Feedback', entry.get('feedback_detail'))}\n\n"
        f"{fmt('📝 Info Tambahan', entry.get('detail_info'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "</pre>"
    )

# Handler /cekdata
# Handler untuk /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_last_30_days_data()

    if not data:
        await update.message.reply_text("📭 Tidak ada data dalam 30 hari terakhir.")
        return

    # Kirim masing-masing entry sebagai pesan terpisah (maks 30)
    for i, entry in enumerate(data[:30], start=1):
        message = format_data(entry)
        await update.message.reply_text(message, parse_mode="HTML")
