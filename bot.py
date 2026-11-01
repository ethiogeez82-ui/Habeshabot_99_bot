import os
import random
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"ሰላም {user_name}! ወደ አውቶማቲክ የቢንጎ ቦት (ከ 1 እስከ 600) በደህና መጡ።\n\n"
        "ጨዋታውን ለመጀመር እና ቁጥር ለማውጣት /bingo የሚለውን ትዕዛዝ ይጠቀሙ!"
    )

async def bingo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drawn_number = random.randint(1, 600)
    await update.message.reply_text(
        f"🎲 **የቢንጎ ዕጣ ቁጥር** 🎲\n\n"
        f"ወጣው ቁጥር: **{drawn_number}** (ከ 1 እስከ 600)\n\n"
        f"እስቲ ካርዳችሁን እዩ!"
    )

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("እባክዎ የቦት ቶከን (BOT_TOKEN) ያስገቡ!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bingo", bingo))

    print("ቦቱ በመጀመር ላይ ነው...")
    app.run_polling()

if __name__ == '__main__':
    main()
