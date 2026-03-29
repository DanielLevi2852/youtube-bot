import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('הבוט במצב "הסוואת אייפון" 📱. שלח לי לינק לשיר מיוטיוב!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'): return

    status_msg = await update.message.reply_text('מנסה לעקוף את החסימה... 🛡️')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song_%(id)s.%(ext)s',
        'noplaylist': True,
        # כאן אנחנו "מתחפשים" לאייפון
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # הוספת "המתנה" קטנה כדי להיראות אנושי יותר
            await asyncio.sleep(2) 
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        await status_msg.edit_text('הצלחתי! שולח שיר... 🚀')
        with open(filename, 'rb') as f:
            await update.message.reply_audio(audio=f, title=info.get('title'))
        
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text("עדיין חסום ❌. יוטיוב מזהה את השרת. כנראה שחייבים לרענן את ה-cookies ב-GitHub.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
