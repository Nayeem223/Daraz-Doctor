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

user_data = {}
waiting_photo = set()
waiting_text = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Use /post to create a post."
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

    if user_id not in waiting_photo:
        return

    user_data[user_id] = {
        "photo": update.message.photo[-1].file_id
    }

    waiting_photo.remove(user_id)
    waiting_text.add(user_id)

    await update.message.reply_text(
        "📝 Now send your full description.\n\n"
        "Write anything you want.\n"
        "Your affiliate link can also be inside the description."
    )


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in waiting_text:
        return

    waiting_text.remove(user_id)

    user_data[user_id]["caption"] = update.message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Publish",
                callback_data="publish"
            ),
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel"
            )
        ]
    ])

    await update.message.reply_photo(
        photo=user_data[user_id]["photo"],
        caption=user_data[user_id]["caption"],
        reply_markup=keyboard
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
            caption="❌ Cancelled."
        )

        return

    if query.data == "publish":

        data = user_data[user_id]

        for channel in CHANNELS:

            await context.bot.send_photo(
                chat_id=channel,
                photo=data["photo"],
                caption=data["caption"]
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
            receive_text
        )
    )

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    app.run_polling()


if __name__ == "__main__":
    main()

