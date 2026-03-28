import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# טוקן הבוט שלך
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['עזרה ❓', 'אודות ℹ️'], ['מחק קבצים זמניים 🧹']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('שלום! אני מוכן להוריד סרטונים. שלח לי לינק!', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == 'עזרה ❓':
        await update.message.reply_text('שלח לי קישור מיוטיוב ואני אוריד אותו כקובץ וידאו.')
        return
    elif text == 'אודות ℹ️':
        await update.message.reply_text('בוט הורדות יוטיוב אישי.')
        return
    elif text == 'מחק קבצים זמניים 🧹':
        await update.message.reply_text('מנקה...')
        return

    if not text.startswith('http'):
        await update.message.reply_text('זה לא קישור תקין...')
        return

    status = await update.message.reply_text('מעבד... ⏳')

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'download_video_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        await status.edit_text('שולח וידאו... 🚀')
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=info.get('title', 'Video'))
        os.remove(filename)
    except Exception as e:
        await status.edit_text(f'שגיאה: {str(e)}')

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    application.run_polling()
