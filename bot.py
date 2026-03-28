import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# הטוקן החדש והמעודכן מהתמונה שלך
TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פקודת ההתחלה של הבוט"""
    await update.message.reply_text('שלום דניאל! הבוט מחובר ועובד עם הטוקן החדש. שלח לי הודעה כלשהי!')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """פונקציה שפשוט מחזירה למשתמש את מה שהוא כתב"""
    user_text = update.message.text
    await update.message.reply_text(f'קיבלתי את ההודעה שלך: {user_text}')

if __name__ == '__main__':
    # בניית האפליקציה
    app = ApplicationBuilder().token(TOKEN).build()
    
    # הוספת הטיפול בפקודות והודעות
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    print("הבוט פועל כעת ב-Render...")
    app.run_polling()
