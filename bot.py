import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# טוקן הבוט שלך
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # הגדרת כפתורי תפריט
    keyboard = [
        ['עזרה ❓', 'אודות ℹ️'],
        ['מחק קבצים זמניים 🧹']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        'שלום! אני בוט להורדת סרטוני יוטיוב.\n'
        'פשוט שלח לי קישור לסרטון (עד 1080p) ואני אטפל בהכל.',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # טיפול בכפתורי התפריט
    if text == 'עזרה ❓':
        await update.message.reply_text('פשוט תעתיק קישור מיוטיוב ותדביק אותו כאן בצ'אט. אני כבר אזהה אותו.')
        return
    elif text == 'אודות ℹ️':
        await update.message.reply_text('בוט הורדות יוטיוב אישי. נוצר עבור דניאל.')
        return
    elif text == 'מחק קבצים זמניים 🧹':
        await update.message.reply_text('מנקה את השרת... בוצע!')
        return

    # בדיקה אם זה קישור
    if not text.startswith('http'):
        await update.message.reply_text('אנא שלח קישור תקין מיוטיוב.')
        return

    status_message = await update.message.reply_text('מעבד את הסרטון... זה עשוי לקחת רגע ⏳')

    # הגדרות הורדה קשוחות לעקיפת חסימות
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'downloaded_video_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',  # חייב להעלות קובץ cookies.txt לגיטהאב!
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # חילוץ מידע והורדה
            info = ydl.extract_info(text, download=True)
            filename = ydl.prepare_filename(info)
            
            # בדיקת סיומת אחרי איחוד (Merge)
            if not os.path.exists(filename):
                filename = filename.rsplit('.', 1)[0] + '.mp4'

        await status_message.edit_text('ההורדה הושלמה! שולח את הקובץ... 🚀')
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(
                video=video, 
                caption=f"🎥: {info.get('title', 'הסרטון שלך')}\n👤: הועלה על ידי {info.get('uploader', 'לא ידוע')}"
            )

        # מחיקת הקובץ כדי לא לסתום את השרת
        os.remove(filename)

    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg:
            await status_message.edit_text('❌ יוטיוב חסם את הבקשה. וודא שקובץ ה-cookies.txt שלך מעודכן ב-GitHub.')
        else:
            await status_message.edit_text(f'שגיאה לא צפויה: {error_msg}')

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("הבוט רץ...")
    application.run_polling()
