import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

# פקודת /start - הודעת ברוכים הבאים
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 *שלום {user_name}!* \n\n"
        "אני הבוט של דניאל להורדת שירים מיוטיוב. \n"
        "פשוט שלח לי *לינק* (סרטון או שיר) ואני אהפוך אותו ל-MP3. \n\n"
        "לחץ על ה-Menu כדי לראות מה עוד אני יודע לעשות!"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# פקודת /help - הסבר למשתמש
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ *איך משתמשים בבוט?* \n\n"
        "1. נכנסים ליוטיוב ומעתיקים לינק לשיר שאתם אוהבים. \n"
        "2. מדביקים את הלינק כאן בצ'אט. \n"
        "3. מחכים כמה שניות... והשיר אצלכם! 🎵"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# פקודת /about - קצת קרדיט
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = "🤖 *על הבוט:* \n\nנוצר על ידי דניאל לוי 🚀 \nהבוט מופעל על שרת Render ומאפשר הורדה מהירה של מוזיקה מיוטיוב."
    await update.message.reply_text(about_text, parse_mode='Markdown')

# טיפול בהורדת שירים (הקוד שכתבנו קודם עם הסוואת האייפון)
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'): return

    status_msg = await update.message.reply_text('מנסה להוריד את השיר... 🎵')

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song_%(id)s.%(ext)s',
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'quiet': True,
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        await status_msg.edit_text('הנה השיר שלך! 🚀')
        with open(filename, 'rb') as f:
            await update.message.reply_audio(audio=f, title=info.get('title'))
        
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await status_msg.edit_text("עדיין חסום ❌. יוטיוב מזהה את השרת. נסה לרענן את ה-cookies.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # חיבור כל הפקודות לפונקציות שלהן
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('about', about_command))
    
    # טיפול בלינקים (כל טקסט שהוא לא פקודה)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_youtube))
    
    print("הבוט פועל עם תפריט ותשובות לפקודות!")
    app.run_polling()
