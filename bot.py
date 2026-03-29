import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('הבוט חזר לחיים! שלח לי לינק קצר לבדיקה (עד 5 דקות).')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'): return

    status_msg = await update.message.reply_text('מעבד בזהירות... ⚙️')

    # הגדרות סופר-קלות כדי למנוע קריסה
    ydl_opts = {
        # מוריד רק וידאו משולב באיכות בינונית (360p/480p) כדי לא לחנוק את השרת
        'format': 'best[height<=480]', 
        'outtmpl': 'vid_%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True, # פחות לוגים = פחות זיכרון
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        # הפעלת ההורדה בצורה שלא תתקע את כל הבוט
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)

        await status_msg.edit_text('שולח לטלגרם... 🚀')
        
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption=info.get('title', 'Ready!'))
        
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        error_str = str(e)
        if "Sign in" in error_str:
            await status_msg.edit_text("יוטיוב דורש אימות. צריך לעדכן את קובץ ה-cookies.")
        else:
            await status_msg.edit_text(f"השרת התעייף: {error_str[:50]}...")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
