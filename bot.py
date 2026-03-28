import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# הטוקן החדש שלך
TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('שלום דניאל! אני מוכן. שלח לי לינק מיוטיוב (סרטון או שיר) ואנסה להוריד אותו עבורך.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # בדיקה אם זה בכלל לינק
    if not url.startswith('http'):
        await update.message.reply_text('זה לא נראה כמו לינק תקין. שלח לי קישור מיוטיוב.')
        return

    status_msg = await update.message.reply_text('מתחיל לעבד את הסרטון... ⏳')

    # הגדרות ההורדה - הגבלנו לאיכות טובה אבל לא כבדה מדי כדי שלא יקרוס
    ydl_opts = {
        'format': 'best', 
        'outtmpl': 'video_%(id)s.%(ext)s',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    # שימוש בקובץ עוגיות אם קיים (למניעת חסימות מיוטיוב)
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        # הורדת הסרטון
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status_msg.edit_text('ההורדה הושלמה! שולח את הקובץ לטלגרם... 🚀')
        
        # שליחת הקובץ לטלגרם
        with open(filename, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=info.get('title', 'הסרטון שלך מוכן!'))
        
        # מחיקת הקובץ מהשרת אחרי השליחה (כדי שלא יתמלא הזיכרון)
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text(f'מצטער, קרתה שגיאה: {str(e)}')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("הבוט פועל ומחכה ללינקים...")
    app.run_polling()
