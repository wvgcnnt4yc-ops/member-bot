import os
import sqlite3
import threading

from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")

# Database
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER
)
""")

conn.commit()


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    invited_by = None

    if context.args:
        if context.args[0].isdigit():
            invited_by = int(context.args[0])

    if invited_by == user_id:
        invited_by = None

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user_id,)
    )

    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
            (user_id, 0, invited_by)
        )

        if invited_by:
            cursor.execute(
                "UPDATE users SET points = points + 150 WHERE user_id = ?",
                (invited_by,)
            )

        conn.commit()

    await update.message.reply_text(
        "سڵاو 👋\nبەخێربێیت بۆ بۆتەکەی کوردی ❤️"
    )


# /balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute(
        "SELECT points FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    points = result[0] if result else 0

    await update.message.reply_text(
        f"💰 خاڵەکانت: {points}"
    )


# Flask
app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Bot is running!"


def run_web():
    app_web.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000))
    )


# Main
def main():
    if not TOKEN:
        print("BOT_TOKEN is not set!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
