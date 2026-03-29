import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# הטוקן שלך
TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

# פקודת /start - הודעת ברוכים הבאים
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 *שלום {user_name}!* \n\n"
        "אני הבוט של דניאל להורדת שירים מיוטיוב. \n"
        "פשוט שלח לי *לינק* (סרטון או שיר) ואני אהפוך אותו ל-MP3. \n\n"
        "💡 _הבוט מעודכן להגדרות דפדפן חדשות (Chrome 122)._"
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

# פונקציה לטיפול בהורדת שירים
async def handle_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith('http'): return

    status_msg = await update.message.reply_text('מנסה להוריד את השיר... 🎵')

    # הגדרות הורדה מעודכנות לעקיפת חסימות
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song_%(id)s.%(ext)s',
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
    }

    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # השהייה קלה כדי להיראות אנושי
            await asyncio.sleep(1)
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        await status_msg.edit_text('הצלחתי! שולח שיר... 🚀')
        with open(filename, 'rb') as f:
            await update.message.reply_audio(audio=f, title=info.get('title'))
        
        # מחיקת הקובץ מהשרת אחרי השליחה
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        error_msg = str(e)
        if "Sign in" in error_msg:
            await status_msg.edit_text("עדיין חסום ❌. יוטיוב מזהה את השרת. צריך לעדכן את קובץ ה-cookies.txt ב-GitHub.")
        else:
            await status_msg.edit_text(f"שגיאה בהורדה: {error_msg[:100]}")

# הפעלת הבוט
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # הוספת הפקודות
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('about', about_command))
    
    # הוספת המטפל בלינקים
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_youtube))
    
    print("הבוט פועל! המתן להודעות...")
    app.run_polling()
