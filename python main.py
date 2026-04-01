from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import os
import re

TOKEN = "8263307601:AAF0-Y8YZxIMqfEpL4oVdjFsW7eoZukXxng"
ADMIN_ID = 6568634089

CHANNEL_LINKS = {
    "join1": "https://t.me/hzdjdjdndnndfn",
    "join2": "https://t.me/dbnxcmcncncm",
    "join3": "https://t.me/hxjdnfnfncj",
    "join4": "https://t.me/Allearningapp120"
}

OTP_LINK = "https://t.me/Allearningapp120"

data = {}
user_clicks = {}
verified_users = set()

# 🔹 FORMAT NUMBER
def format_numbers(lines):
    numbers = []
    for line in lines:
        num = line.strip()
        if not num:
            continue
        num = "".join(filter(str.isdigit, num))
        num = "+" + num
        numbers.append(num)
    return numbers

# 🔥 LOAD TXT FROM ROOT
def load_all_numbers():
    global data
    data.clear()

    for file in os.listdir():
        if file.endswith(".txt") and file != "users.txt":

            country = file.replace(".txt", "")
            country = re.sub(r"\(\d+\)", "", country).strip()

            with open(file, "r") as f:
                numbers = format_numbers(f.readlines())

            if country not in data:
                data[country] = []

            data[country].extend(numbers)
            data[country] = list(set(data[country]))

# 🔹 SAVE VERIFIED
def save_verified():
    with open("users.txt", "w") as f:
        for uid in verified_users:
            f.write(str(uid) + "\n")

# 🔹 MENU
def menu():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Get Number"), KeyboardButton("Live Stock")],
            [KeyboardButton("Invite & Earn")],
            [KeyboardButton("Support")]
        ],
        resize_keyboard=True
    )

# 🔹 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    load_all_numbers()

    if user.id in verified_users:
        await update.message.reply_text("✅ Numbers Loaded", reply_markup=menu())
        return

    keyboard = [
        [InlineKeyboardButton("📢 Join 1", callback_data="join1"), InlineKeyboardButton("📢 Join 2", callback_data="join2")],
        [InlineKeyboardButton("📢 Join 3", callback_data="join3"), InlineKeyboardButton("📢 Join 4", callback_data="join4")],
        [InlineKeyboardButton("🔄 Verify", callback_data="verify")]
    ]

    await update.message.reply_text(
        "❌ Access Locked!\nClick all 4 buttons then verify.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔹 MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Get Number":
        if not data:
            await update.message.reply_text("❌ No country available")
            return

        buttons = [[InlineKeyboardButton(c, callback_data=c)] for c in data.keys()]
        await update.message.reply_text("Select Country:", reply_markup=InlineKeyboardMarkup(buttons))

    elif text == "Live Stock":
        msg = "📊 STOCK:\n"
        for c in data:
            msg += f"{c}: {len(data[c])}\n"
        await update.message.reply_text(msg)

# 🔹 FILE UPLOAD SYSTEM
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    doc = update.message.document

    if not doc.file_name.endswith(".txt"):
        await update.message.reply_text("❌ Only TXT file allowed")
        return

    file = await doc.get_file()
    file_name = doc.file_name

    await file.download_to_drive(file_name)

    country = file_name.replace(".txt", "")
    country = re.sub(r"\(\d+\)", "", country).strip()

    with open(file_name, "r") as f:
        numbers = format_numbers(f.readlines())

    if country not in data:
        data[country] = []

    data[country].extend(numbers)
    data[country] = list(set(data[country]))

    await update.message.reply_text(
        f"✅ {country}\n{len(numbers)} Numbers Added"
    )

# 🔹 BUTTON
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("join"):
        if user_id not in user_clicks:
            user_clicks[user_id] = set()

        user_clicks[user_id].add(query.data)

        await context.bot.send_message(
            chat_id=user_id,
            text="👉 Open channel:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Open", url=CHANNEL_LINKS[query.data])]
            ])
        )
        return

    if query.data == "verify":
        if len(user_clicks.get(user_id, [])) == 4:
            verified_users.add(user_id)
            save_verified()

            await query.message.delete()

            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Verified!",
                reply_markup=menu()
            )
        else:
            await query.answer("❌ Click all buttons", show_alert=True)
        return

    country = query.data

    if country in data:
        if data[country]:
            number = data[country].pop(0)

            with open(f"{country}.txt", "w") as f:
                for n in data[country]:
                    f.write(n + "\n")

            keyboard = [
                [InlineKeyboardButton("🔄 Next", callback_data=country)],
                [InlineKeyboardButton("💬 Join OTP", url=OTP_LINK)]
            ]

            text = f"""📍 {country}

━━━━━━━━━━━━━━━
📞 `{number}`
━━━━━━━━━━━━━━━

📋 Hold to copy
"""

            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.answer("No numbers left", show_alert=True)

# 🔹 RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
app.add_handler(CallbackQueryHandler(button_click))

print("Bot running...")
app.run_polling()
