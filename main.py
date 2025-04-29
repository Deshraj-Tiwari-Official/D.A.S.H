import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Main Menu Keyboard
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Command List 📜", callback_data='command_list')],
        [InlineKeyboardButton("About 👀", callback_data='about')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Back button row
def back_to_main_row():
    return [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main_menu')]

# Commands Menu (2-column with back button at bottom)
def commands_keyboard():
    keyboard = [
        [InlineKeyboardButton("Reminder 🔔", callback_data='reminder'), InlineKeyboardButton("Weather 🌦️", callback_data='weather')],
        [InlineKeyboardButton("Pomodoro 🍅", callback_data='pomodoro')],
        back_to_main_row()  # ✅ now just one row, no nested list issue
    ]
    return InlineKeyboardMarkup(keyboard)

# Back-only menu for content pages
def back_only_markup():
    return InlineKeyboardMarkup([back_to_main_row()])

# Start Command Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Main Menu 🏠",
        reply_markup=main_menu_keyboard()
    )

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match query.data:
        case "about":
            await query.edit_message_text(
                text="I was made by Dash 😎. I'm here to assist you with my configured commands!",
                reply_markup=back_only_markup()
            )
        case "command_list":
            await query.edit_message_text(
                text="Here is the list of available commands:",
                reply_markup=commands_keyboard()
            )
        case "main_menu":
            await query.edit_message_text(
                text="Main Menu 🏠",
                reply_markup=main_menu_keyboard()
            )
        case "reminder":
            await query.edit_message_text(
                text="⏰ Reminder functionality is coming soon!",
                reply_markup=back_only_markup()
            )
        case "weather":
            await query.edit_message_text(
                text="🌦️ Weather feature coming soon!",
                reply_markup=back_only_markup()
            )
        case "pomodoro":
            await query.edit_message_text(
                text="🍅 Pomodoro timer feature coming soon!",
                reply_markup=back_only_markup()
            )

# Run App
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
