import logging
import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# הטוקן שלך
TOKEN = '8777569297:AAFXSfYINq4p36qVcYcClcQD0h-xAyR8UQU'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("אהלן דניאל! שלח לי לינק מיוטיוב ובחר את האיכות הרצויה. 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("נא לשלוח לינק תקין מיוטיוב.")
        return

    context.user_data['current_url'] = url

    # יצירת כפתורי בחירה: 4 איכויות וידאו ו-2 אפשרויות שמע
    keyboard = [
        [InlineKeyboardButton("🎬 וידאו - Full HD (1080p)", callback_data='video_1080')],
        [InlineKeyboardButton("🎬 וידאו - HD (720p)", callback_data='video_720')],
        [InlineKeyboardButton("🎬 וידאו - SD (480p)", callback_data='video_480')],
        [InlineKeyboardButton("🎬 וידאו - Low (360p)", callback_data='video_360')],
        [InlineKeyboardButton("🎵 שמע - MP3 (איכות גבוהה 320kbps)", callback_data='audio_320')],
        [InlineKeyboardButton("🎵 שמע - MP3 (סטנדרטי 128kbps)", callback_data='audio_128')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("בחר פורמט ואיכות להורדה:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('current_url')
    choice = query.data
    chat_id = query.message.chat_id

    if not url:
        await query.edit_message_text("פג תוקף הבקשה, שלח לינק מחדש.")
        return

    status_msg = await query.edit_message_text("בודק נתונים ומתחיל הורדה... ⏳")

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        mode = 'video'
        if choice.startswith('video'):
            height = choice.split('_')[1]
            # הגדרה להורדת וידאו באיכות נבחרת ומיזוג עם FFmpeg
            ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': 'downloaded_video.%(ext)s',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        else: # שמע MP3
            quality = choice.split('_')[1]
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
            }
            mode = 'audio'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == 'audio':
                filename = os.path.splitext(filename)[0] + ".mp3"

        # בדיקת גודל הקובץ (מגבלת טלגרם לבוטים היא 50MB)
        filesize_mb = os.path.getsize(filename) / (1024 * 1024)
        
        if filesize_mb > 50:
            await status_msg.edit_text(f"❌ הקובץ גדול מדי ({filesize_mb:.1f}MB). טלגרם מאפשרת עד 50MB. נסה איכות נמוכה יותר.")
            os.remove(filename)
            return

        await status_msg.edit_text(f"מעלה קובץ בגודל {filesize_mb:.1f}MB... 📤")
        
        with open(filename, 'rb') as f:
            if mode == 'video':
                await context.bot.send_video(chat_id=chat_id, video=f, caption=info.get('title'))
            else:
                await context.bot.send_audio(chat_id=chat_id, audio=f, title=info.get('title'))

        os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"שגיאה: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("בוטיוטיוב המשודרג באוויר! (1080p, MP3 ובדיקת נפח)")
    app.run_polling()

if __name__ == '__main__':
    main()
