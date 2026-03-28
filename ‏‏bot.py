import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# טוקן הבוט שלך
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('הבוט עובד! שלח לי הודעה כלשהי.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # הבוט פשוט יחזיר לך את מה שכתבת לו
    user_text = update.message.text
    await update.message.reply_text(f'קיבלתי את ההודעה שלך: {user_text}')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    print("Bot is running...")
    app.run_polling()
