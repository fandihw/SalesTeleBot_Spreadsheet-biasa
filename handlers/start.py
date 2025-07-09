from telegram import Update
from telegram.ext import ContextTypes

WELCOME = (
    "👋 Selamat datang di *Sales Visit Bot*.\n\n"
    "Gunakan /start untuk memulai input baru.\n"
    "Gunakan /cekdata untuk melihat 30 data terakhir."
)

HELP = (
    "🛠 *Bantuan*\n"
    "• /start – memulai input kunjungan\n"
    "• /cekdata – menampilkan 30 data terakhir\n"
)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = "kategori"
    from handlers.form import ask_next
    await update.message.reply_text(WELCOME, parse_mode="Markdown")
    # Langsung masuk step pertama
    await ask_next(update, context)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, parse_mode="Markdown")
