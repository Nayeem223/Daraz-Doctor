from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, OWNER_ID, CHANNELS

waiting_photo = set()
waiting_details = set()

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "👋 Welcome to Daraz Doctor\n\n"
        "Use /post to create a new post."
    )


async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    waiting_photo.add(update.effective_user.id)

    await update.message.reply_text(
        "📸 Send Product Photo"
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        return

    if user_id not in waiting_photo:
        return

    photo = update.message.photo[-1].file_id

    user_data[user_id] = {
        "photo": photo
    }

    waiting_photo.remove(user_id)
    waiting_details.add(user_id)

    await update.message.reply_text(
        "📝 Send Product Details\n\n"
        "Example:\n\n"
        "Product Name: Redmi Buds 6\n"
        "Price: ৳1399\n"
        "Offer: 35% OFF\n"
        "Link: https://yourlink.com"
    )

async def receive_details(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        return

    if user_id not in waiting_details:
        return

    text = update.message.text

    product = ""
    price = ""
    offer = ""
    link = ""

    for line in text.split("\n"):

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.lower().strip()
        value = value.strip()

        if key == "product name":
            product = value

        elif key == "price":
            price = value

        elif key == "offer":
            offer = value

        elif key == "link":
            link = value

    user_data[user_id]["product"] = product
    user_data[user_id]["price"] = price
    user_data[user_id]["offer"] = offer
    user_data[user_id]["link"] = link

    waiting_details.remove(user_id)

    caption = (
        "━━━━━━━━━━━━━━\n\n"
        f"🔥 {product}\n\n"
        f"💰 Price: {price}\n\n"
        f"🎁 Offer: {offer}\n\n"
        "━━━━━━━━━━━━━━"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Buy Now",
                url=link
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Publish",
                callback_data="publish"
            ),
            InlineKeyboardButton(
                "✏️ Edit",
                callback_data="edit"
            ),
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel"
            ),
        ]
    ]

    await update.message.reply_photo(
        photo=user_data[user_id]["photo"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id != OWNER_ID:
        return

    if query.data == "cancel":

        user_data.pop(user_id, None)

        await query.edit_message_caption(
            caption="❌ Post Cancelled."
        )

    elif query.data == "edit":

        waiting_details.add(user_id)

        await query.message.reply_text(
            "📝 Send Product Details Again"
        )

    elif query.data == "publish":

        data = user_data[user_id]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🛒 Buy Now",
                    url=data["link"]
                )
            ]
        ])

        caption = (
            "━━━━━━━━━━━━━━\n\n"
            f"🔥 {data['product']}\n\n"
            f"💰 Price: {data['price']}\n\n"
            f"🎁 Offer: {data['offer']}\n\n"
            "━━━━━━━━━━━━━━"
        )

        for channel in CHANNELS:
            await context.bot.send_photo(
                chat_id=channel,
                photo=data["photo"],
                caption=caption,
                reply_markup=keyboard
            )

        user_data.pop(user_id, None)

        await query.edit_message_caption(
            caption="✅ Successfully Published!"
        )

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receive_photo
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_details
        )
    )

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
