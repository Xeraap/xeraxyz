import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary untuk menyimpan pasangan yang sedang chatting
current_matches = {}
# Menyimpan status pengguna apakah mereka dalam pencarian atau tidak
waiting_for_match = set()

# Fungsi untuk mencari pasangan baru dan memulai percakapan
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in current_matches:  # Ganti 'users' menjadi 'current_matches'
        current_matches[user_id] = None
        await update.message.reply_text('Ketik /search untuk mencari teman ngobrol.')
    else:
        await update.message.reply_text('Anda masih terhubung dengan seseorang.\n\n/next | mengganti pasangan.\n/stop | menghentikan percakapan.')

async def search(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    
    # Cek apakah pengguna sudah terhubung dengan seseorang
    if current_matches.get(user_id) is not None:
        matched_user = current_matches[user_id]
        del current_matches[user_id]
        del current_matches[matched_user]
        await update.message.reply_text("Anda telah berhenti dari percakapan sebelumnya.")
        await context.bot.send_message(matched_user, "Pasangan Anda telah berhenti chatting. Anda dapat mencari pasangan lain dengan menggunakan /search .")
    
    # Cek apakah ada pasangan yang sedang menunggu
    if waiting_for_match:
        matched_user = waiting_for_match.pop()  # Ambil pengguna yang sedang menunggu
        current_matches[user_id] = matched_user
        current_matches[matched_user] = user_id
        
        await update.message.reply_text(f"Anda terhubung dengan seseorang! Anda bisa mulai chatting.\n\n/next | mengganti pasangan.\n/stop | menghentikan percakapan.")
        await context.bot.send_message(matched_user, f"Anda terhubung dengan seseorang. Mulai chatting sekarang! \n\n/next | mengganti pasangan.\n/stop | menghentikan percakapan.")
    else:
        # Jika tidak ada pengguna yang menunggu, tambahkan pengguna ke dalam antrean
        waiting_for_match.add(user_id)
        await update.message.reply_text("Menunggu pasangan lain. Anda akan terhubung segera setelah ada pengguna lain yang mencari pasangan.")

# Fungsi untuk mengganti pasangan yang sedang terhubung
async def next(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    
    # Jika pengguna sudah terhubung dengan seseorang, putuskan pasangan tersebut
    if current_matches.get(user_id) is not None:
        matched_user = current_matches[user_id]
        del current_matches[user_id]
        del current_matches[matched_user]
        await update.message.reply_text("Anda telah berhenti dari percakapan sebelumnya.")
        await context.bot.send_message(matched_user, "Pasangan Anda telah berhenti chatting. Anda dapat mencari pasangan lain dengan menggunakan /search.")
    
    # Mencari pasangan baru
    available_users = [user for user, match in current_matches.items() if match is None and user != user_id]
    
    if available_users:
        # Pilih pasangan secara acak
        matched_user = random.choice(available_users)
        current_matches[user_id] = matched_user
        current_matches[matched_user] = user_id
        
        await update.message.reply_text(f"Anda terhubung dengan seseorang! Anda bisa mulai chatting.\n\n/next | mengganti pasangan.\n/stop | menghentikan percakapan.")
        await context.bot.send_message(matched_user, f"Anda terhubung dengan seseorang. Mulai chatting sekarang!\n\n/next | mengganti pasangan.\n/stop | menghentikan percakapan.")
    else:
        await update.message.reply_text("Tidak ada pengguna lain yang tersedia saat ini. Coba lagi nanti.")

# Fungsi untuk berhenti dan melepaskan pasangan
async def stop(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    if user_id in current_matches and current_matches[user_id] is not None:
        matched_user = current_matches[user_id]
        del current_matches[user_id]
        del current_matches[matched_user]
        await update.message.reply_text("Anda telah keluar dari pasangan chat. Gunakan /search untuk mencari pasangan baru.")
        await context.bot.send_message(matched_user, "Pasangan Anda telah berhenti chatting. Gunakan /search untuk mencari pasangan lain.")
    else:
        await update.message.reply_text("Anda belum terhubung dengan siapa pun.")

# Fungsi untuk menangani pesan chat
async def chat_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    if user_id in current_matches and current_matches[user_id] is not None:
        matched_user = current_matches[user_id]
        await context.bot.send_message(matched_user, update.message.text)

# Fungsi utama untuk menjalankan bot
def main():
    # Gantilah dengan token bot yang Anda dapatkan dari BotFather
    token = "7657719355:AAHrAGlZ0NTa7U6UgnU70fFrWXq0jm6kCcI"
    
    application = Application.builder().token(token).build()
    
    # Handler perintah
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))  # /search untuk mulai percakapan dan mencari pasangan
    application.add_handler(CommandHandler("next", next))  # /next untuk mengganti pasangan
    application.add_handler(CommandHandler("stop", stop))  # /stop untuk berhenti dari percakapan
    
    # Handler pesan chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    
    # Mulai bot
    application.run_polling()

if __name__ == '__main__':
    main()
