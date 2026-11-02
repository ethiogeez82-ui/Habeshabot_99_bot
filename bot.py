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
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationBuilder

# 1. ዳታቤዝ ማዘጋጀት (Database Setup)
def init_db():
    conn = sqlite3.connect('bingo_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

# ቦቱ ሲነሳ ዳታቤዙን ማዘጋጀት
init_db()

# 2. የሒሳብ መጠን ማሳያ ትዕዛዝ (/balance)
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    conn = sqlite3.connect('bingo_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row:
        balance = row[0]
    else:
        # አዲስ ተጠቃሚ ሲመዘገብ
        cursor.execute('INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)', 
                       (user_id, username, 0.0))
        conn.commit()
        balance = 0.0
        
    conn.close()
    await update.message.reply_text(f"💳 የእርስዎ የኪስ ቦርሳ ሒሳብ: *{balance} ብር* ነው።", parse_mode="Markdown")

# 3. ገንዘብ ለመሙላት የሚጠየቅ ትዕዛዝ (/deposit)
async def deposit_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deposit_text = (
        "💰 *ብር ለመሙላት (Deposit):*\n\n"
        "እባክዎ ከታች ባሉት አካውንቶች ገንዘብ ገቢ በማድረግ ደረሰኙን (Screenshot) ወይም የግብይት ቁጥር ይላኩ:\n\n"
        "🏦 *ንግድ ባንክ:* 1000XXXXXXXXXX\n"
        "📱 *ቴሌብር (Telebirr):* 0912345678\n\n"
        "ክፍያውን ከፈጸሙ በኋላ ማረጋገጫውን ለአስተዳዳሪው ይላኩ። ሒሳብዎ ወዲያውኑ ይስተካከላል!"
    )
    await update.message.reply_text(deposit_text, parse_mode="Markdown")

# 4. ለአስተዳዳሪ የሰውየውን ሒሳብ ለመጨመር (/addbalance [user_id] [amount])
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # የእርስዎን የአስተዳዳሪ ቴሌግራም ID እዚህ ያስገቡ (ለምሳሌ: 123456789)
      485838791
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("ይህንን ትዕዛዝ ለመጠቀም ፈቃድ የለዎትም!")
        return

    try:
        args = context.args
        target_user_id = int(args[0])
        amount = float(args[1])

        conn = sqlite3.connect('bingo_bot.db')
        cursor = conn.cursor()
        
        # ተጠቃሚው መኖሩን አረጋግጦ ሒሳብ መጨመር
        cursor.execute('UPDATE users SET balance = balance + ? W፦HERE user_id = ?', (amount, target_user_id))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ ለተጠቃሚ {target_user_id} ሒሳብ *{amount} ብር* በተሳካ ሁኔታ ተጨምሯል!", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("አጠቃቀም ስህተት አለው። ትክክለኛው: /addbalance [user_id] [amount]")
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("እባክዎ የቦት ቶከን (BOT_TOKEN) ያስገቡ")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # ትዕዛዞችን እዚህ መዝግቡ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bingo", bingo))
    app.add_handler(CommandHandler("balance", check_balance))
    app.add_handler(CommandHandler("deposit", deposit_money))
    app.add_handler(CommandHandler("addbalance", add_balance))

    print("ቦቱ በመጀመር ላይ ነው ...")
    app.run_polling()

if __name__ == '__main__':
    main()
