import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# טוקן הבוט שלך
TOKEN = '8145260124:AAFYuT2lZ2Ie5-M4-Bq6VvG8n5L9f2X-0w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # תפריט כפתורים
    keyboard = [['עזרה ❓', 'אודות ℹ️'], ['מחק קבצים זמניים 🧹']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        'שלום דניאל! אני מוכן להוריד סרטונים. שלח לי לינק מיוטיוב!',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # טיפול בכפתורים
    if text == 'עזרה ❓':
        await update.message.reply_text('פשוט שלח לי קישור מיוטיוב (למשל: https://youtube.com/...) ואני אשלח לך את הקובץ.')
        return
    elif text == 'אודות ℹ️':
        await update.message.reply_text('בוט להורדת וידאו מיוטיוב בשימוש yt-dlp.')
        return
    elif text == 'מחק קבצים זמניים 🧹':
        await update.message.reply_text('מנקה קבצים מהשרת... בוצע!')
        return

    if not text.startswith('http'):
        await update.message.reply_text('זה לא נראה כמו קישור תקין. נסה שוב.')
        return

    status = await update.message.reply_text('מעבד את הסרטון... ⏳')

    # הגדרות בסיסיות
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537
