import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# הכנס כאן את הטוקן שקיבלת מה-BotFather
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('שלום דניאל! שלח לי קישור מיוטיוב ואני אוריד אותו עבורך.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'):
        await update.message.reply_text('זה לא נראה כמו קישור תקין...')
        return

    status_message = await update.message.reply_text('מעבד את הבקשה, אנא המתן...')

    # הגדרות הורדה מעודכנות לעקיפת חסימות
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'downloaded_video.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'cookies.txt',  # וודא שהעלית קובץ כזה ל-GitHub!
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # אם הקובץ אוחד ל-mp4, השם עלול להשתנות
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        await status_message.edit_text('ההורדה הושלמה! שולח את הקובץ...')
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption=info.get('title', 'הסרטון שלך'))

        # מחיקת הקובץ מהשרת אחרי השליחה כדי לחסוך מקום
        os.remove(filename)

    except Exception as e:
        await status_message.edit_text(f'שגיאה: {str(e)}')

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("הבוט פועל...")
    application.run_polling()
