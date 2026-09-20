import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

    cur = db.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
    exists = cur.fetchone()

    if not exists:
        inviter = None

        if args and args[0].isdigit():
            inviter = int(args[0])
            if inviter != user.id:
                db.execute(
                    "UPDATE users SET points = points + 150 WHERE user_id=?",
                    (inviter,)
                )

        db.execute(
            "INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
            (user.id, 0, inviter)
        )
        db.commit()

    link = f"https://t.me/{context.bot.username}?start={user.id}"

    await update.message.reply_text(
        f"👋 بەخێربێیت {user.first_name}!\n\n"
        f"🪙 بۆ بینینی خاڵەکانت:\n/balance\n\n"
        f"🔗 لینکی بانگهێشتکردنت:\n{link}\n\n"
        f"👥 هەر کەسێک بە لینکی تۆ بێت، 150 خاڵ بۆ تۆ زیاد دەبێت."
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cur = db.execute(
        "SELECT points FROM users WHERE user_id=?",
        (user_id,)
    )
    row = cur.fetchone()

    points = row[0] if row else 0

    await update.message.reply_text(
        f"🪙 خاڵەکانت: {points}"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))

    app.run_polling()


if __name__ == "__main__":
    main()
