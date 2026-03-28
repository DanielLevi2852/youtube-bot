import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['עזרה ❓', 'אודות ℹ️'], ['מחק קבצים זמניים 🧹']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('שלום! שלח לי קישור מיוטיוב להורדה.', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'):
        return

    status = await update.message.reply_text('מעבד... ⏳')

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        await status.edit_text('שולח... 🚀')
        with open(filename, 'rb') as v:
            await update.message.reply_video(video=v, caption=info.get('title', 'Video'))
        os.remove(filename)
    except Exception as e:
        await status.edit_text(f'שגיאה: {str(e)}')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is up!")
    app.run_polling()