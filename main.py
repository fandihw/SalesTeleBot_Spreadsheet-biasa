from config import BOT_TOKEN
from handlers import start, form, photo, cekdata

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ───── Command ─────
    app.add_handler(CommandHandler("start", start.start_cmd))
    app.add_handler(CommandHandler("help",  start.help_cmd))
    app.add_handler(CommandHandler("cekdata", cekdata.handle_cekdata))

    # ───── Callback Inline Keyboard ─────
    app.add_handler(CallbackQueryHandler(form.handle_callback, pattern="^(?!confirm_data|cancel_data).*"))  # Semua selain confirm/cancel
    app.add_handler(CallbackQueryHandler(form.handle_confirmation, pattern="^(confirm_data|cancel_data)$"))

    # Teks normal (jawaban form)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, form.handle_text))  # Tetap, tapi di bawah

    # ───── Upload Foto ─────
    app.add_handler(MessageHandler(filters.PHOTO, form.handle_photo))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
