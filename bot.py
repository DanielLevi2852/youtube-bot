import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# זהו ה"מפתח" הייחודי של הבוט שלך שקיבלת מ-BotFather
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

# פונקציה שמופעלת כשכותבים לבוט /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('דניאל, הבוט התעורר לחיים! הכל נקי ועובד.')

if __name__ == '__main__':
    # בניית האפליקציה של הבוט
    app = ApplicationBuilder().token(TOKEN).build()
    
    # חיבור הפקודה /start לפונקציה שכתבנו למעלה
    app.add_handler(CommandHandler('start', start))
    
    # התחלת האזנה להודעות
    print("הבוט התחיל לעבוד...")
    app.run_polling()
