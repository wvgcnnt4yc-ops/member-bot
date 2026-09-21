import os
import sqlite3
import threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")

db = sqlite3.connect("users.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER
)
""")
db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    invited_by = None
    if args and args[0].isdigit():
        invited_by = int(args[0])
        if invited_by == user.id:
            invited_by = None

    cur = db.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
            (user.id, 0, invited_by)
        )

        if invited_by:
            cur.execute(
                "UPDATE users SET points = points + 150 WHERE user_id = ?",
                (invited_by,)
            )

        db.commit()

    await update.message.reply_text(
        "سڵاو 👋\n\n"
        "بەخێربێیت بۆ Member Bot 🤖\n\n"
        "👤 بۆ بانگهێشتکردنی کەسانی تر:\n"
        "لینکی بانگهێشت بەکاربهێنە.\n\n"
        "💰 بۆ بینینی خاڵەکانت:\n"
        "/balance"
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cur = db.cursor()
    cur.execute(
        "SELECT points FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()

    points = row[0] if row else 0

    await update.message.reply_text(
        f"💰 خاڵەکانت: {points}"
    )

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    threading.Thread(target=run_web, daemon=True).start()
    app.run_polling()


if __name__ == "__main__":
    main()
