import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

scheduler = BackgroundScheduler()
scheduler.start()

user_pomodoro_jobs = {}


# === Keyboard Layouts ===
def back_to_main_row():
    return InlineKeyboardButton("Main Menu", callback_data='menu_main')


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Command List 📜", callback_data='menu_commands')],
        [InlineKeyboardButton("About 👀", callback_data='menu_about')]
    ])


def commands_keyboard():
    keyboard = [
        [InlineKeyboardButton("Pomodoro 🍅", callback_data='cmd_pomodoro')],
        [back_to_main_row()]  # Added main menu button here
    ]
    return InlineKeyboardMarkup(keyboard)


def pomodoro_keyboard(include_stop=False):
    if include_stop:
        keyboard = [[InlineKeyboardButton("🛑 Stop Pomodoro", callback_data='pomodoro_stop')]]
    else:
        keyboard = [
            [InlineKeyboardButton("25m", callback_data='pomodoro_25'),
             InlineKeyboardButton("40m", callback_data='pomodoro_40'),
             InlineKeyboardButton("55m", callback_data='pomodoro_55')]
        ]
    # Always add the main menu button in both cases
    keyboard.append([back_to_main_row()])
    return InlineKeyboardMarkup(keyboard)


# === Callback Routing Logic ===
def route_callback(data):
    if data.startswith("menu_"):
        return handle_menu_callback
    elif data.startswith("cmd_"):
        return handle_command_callback
    elif data.startswith("pomodoro_"):
        return handle_pomodoro_callback
    return handle_unknown_callback


# === Menu & Command Callbacks ===
async def handle_menu_callback(query, context):
    match query.data:
        case "menu_about":
            await query.edit_message_text(
                text=(
                    "👋 Hey there! I'm *D.A.S.H*, your no-nonsense productivity sidekick ⚡️.\n\n"
                    "🔥 Built with Python, backed by Telegram, and coded by the legend *Dash* 😎.\n\n"
                    "📜 Check out commands to explore features.\n\n"
                    "_Designed for students, developers, hustlers, and chaos goblins alike._"
                ),
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [back_to_main_row()]
                ])
            )
        case "menu_commands":
            await query.edit_message_text(
                text="Here is the list of available commands:",
                reply_markup=commands_keyboard()
            )
        case "menu_main":
            # Ensure the text updates to "Main Menu" when clicking on "Main Menu" button
            if query.message.text != "Main Menu":
                await query.edit_message_text(
                    text="Welcome back to the Main Menu! Choose an option:",
                    reply_markup=main_menu_keyboard()
                )


async def handle_command_callback(query, context):
    user_id = query.from_user.id
    match query.data:
        case "cmd_pomodoro":
            include_stop = user_id in user_pomodoro_jobs
            await query.edit_message_text(
                text="Select your Pomodoro duration ⏳",
                reply_markup=pomodoro_keyboard(include_stop=include_stop)
            )


async def handle_pomodoro_callback(query, context):
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    if query.data == "pomodoro_stop":
        if user_id in user_pomodoro_jobs:
            for job in user_pomodoro_jobs[user_id]:
                job.remove()
            del user_pomodoro_jobs[user_id]
        await query.edit_message_text(
            text="🛑 Pomodoro stopped.",
            reply_markup=pomodoro_keyboard(include_stop=False)
        )
        return

    duration = int(query.data.split("_")[1])
    await query.edit_message_text(
        text=f"🍅 Pomodoro in Progress - {duration} min",
        reply_markup=pomodoro_keyboard(include_stop=True)
    )
    schedule_pomodoro_cycle(user_id, chat_id, duration, context)


async def handle_unknown_callback(query, context):
    await query.edit_message_text("Unknown option selected.")


# === Pomodoro Logic ===
def schedule_pomodoro_cycle(user_id, chat_id, duration, context):
    loop = asyncio.get_event_loop()

    async def send_async_msg(text):
        await context.bot.send_message(chat_id=chat_id, text=text)

    def run_in_loop(coro):
        asyncio.run_coroutine_threadsafe(coro, loop)

    # 🍅 Focus Start
    scheduler.add_job(lambda: run_in_loop(send_async_msg("🍅 Focus time started!")),
                      trigger='date', run_date=datetime.now())

    # ⏱️ Break Time
    scheduler.add_job(lambda: run_in_loop(send_async_msg("⏱️ Break time! 5 mins.")),
                      trigger='date', run_date=datetime.now() + timedelta(minutes=duration))

    def next_cycle():
        if user_id in user_pomodoro_jobs:
            schedule_pomodoro_cycle(user_id, chat_id, duration, context)

    repeat_job = scheduler.add_job(next_cycle, 'date', run_date=datetime.now() + timedelta(minutes=duration + 5))
    user_pomodoro_jobs[user_id] = [repeat_job]


# === Start & Button Handlers ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="Hi, I am D.A.S.H., Dynamic Assistant System Handler. I would help you by performing certain things too boost your productivity. I am not a machine. I am an emotion. 😄",
        reply_markup=main_menu_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    handler = route_callback(query.data)
    await handler(query, context)

# === Run Bot ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
