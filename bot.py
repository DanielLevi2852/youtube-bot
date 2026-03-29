import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import subprocess

TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

async def handle_spotify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "spotify.com" not in url:
        return

    status_msg = await update.message.reply_text('מנתח את הלינק מספוטיפיי... 🎧')

    try:
        # פקודה להורדת השיר באמצעות spotdl
        # אנחנו משתמשים ב-subprocess כדי להריץ את הכלי ישירות
        process = await asyncio.create_subprocess_exec(
            'spotdl', url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await status_msg.edit_text('מוריד וממיר ל-MP3... זה עשוי לקחת רגע ⏳')
        stdout, stderr = await process.communicate()

        # חיפוש קובץ ה-mp3 שנוצר בתיקייה
        mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
        
        if mp3_files:
            filename = mp3_files[0]
            await status_msg.edit_text('הצלחתי! שולח שיר... 🚀')
            with open(filename, 'rb') as f:
                await update.message.reply_audio(audio=f)
            
            # ניקוי הקובץ
            os.remove(filename)
        else:
            await status_msg.edit_text('שגיאה: לא הצלחתי לייצר קובץ MP3. נסה לינק אחר.')

    except Exception as e:
        await status_msg.edit_text(f"קרתה תקלה: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_spotify))
    print("בוט ספוטיפיי באוויר!")
    app.run_polling()
