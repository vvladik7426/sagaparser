import os
from datetime import timedelta, datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from client_data import ClientData
from database import ClientsDatabaseConnection

# api_token = "7582392341:AAEegcVYFVfBHFAMXVj6eC0o1h893TTBjSs"
api_token = "6546781849:AAGLlxA0Y_Vmc4phKCH7utXE-GTzFy8RVgQ"  # test bot @Person_AI_bot

bot = Bot(api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    with ClientsDatabaseConnection() as db:
        client = db.read_clients().by_telegram_username(message.from_user.username)
        if client is not None and client.immomio_email and client.immomio_password and client.plan_activated_at:
            await message.reply(f"Привіт, {message.from_user.first_name}!\n\n"
                                f"Ви вже активовані.\n"
                                f"Наступна оплата: {(client.plan_activated_at + timedelta(days=30)).strftime('%d.%m.%Y')}\n",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="Підтримка", url="https://t.me/yukothehealer")]
                                ]))
        else:
            await message.reply(f"Вітаю, {message.from_user.first_name}!\n"
"""
Я — бот, який допоможе тобі знайти квартиру на SAGA в Німеччині.
 🏠 Як тільки з’являється нова квартира на сайті SAGA,
 🔔 я миттєво надсилаю тобі повідомлення
 📩 і автоматично подаю заявку за тебе — швидше, ніж це встигне зробити хтось інший!
⚠️ Бот не гарантує отримання квартири, але значно збільшує твої шанси.
👉 Щоб зв’язатися з менеджером та активувати мої можливості, натисни кнопку нижче.
""",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="Підтримка", url="https://t.me/yukothehealer")]
                                ]))
            if client is None:
                db.write_client(ClientData(message.from_user.username))

@dp.message(Command("setclcreds"))
async def setclcreds_handler(message: Message):
    if message.from_user.id == 1909320566:
        args = message.text.split(" ")[1:]
        print("setclcreds args:", args)
        if len(args) >= 3:
            username = args[0].replace('@', '')
            immomio_email = args[1]
            immomio_password = args[2]
            with ClientsDatabaseConnection() as db:
                client = db.read_clients().by_telegram_username(message.from_user.username)
                print(db.read_clients())
                if client is not None:
                    await message.reply(f"== {client}")
                    db.update_immomio_credentials(username, immomio_email, immomio_password)
                    await message.reply(f"~= {db.read_clients().by_telegram_username(message.from_user.username)}")
                else:
                    await message.reply("!= any client")
        else:
            await message.reply(f"Not enough arguments!")

@dp.message(Command("activatecl"))
async def activatecl_handler(message: Message):
    if message.from_user.id == 1909320566:
        args = message.text.split(" ")[1:]
        print("activatecl args:", args)
        if len(args) >= 1:
            username = args[0].replace('@', '')
            with ClientsDatabaseConnection() as db:
                client = db.read_clients().by_telegram_username(username)
                if client is not None:
                    await message.reply(f"== {client}")
                    db.update_plan_activated_at(client.telegram_username, datetime.now())
                    await message.reply(f"~= {db.read_clients().by_telegram_username(username)}")
                else:
                    await message.reply(f"!= any client")
        else:
            await message.reply(f"Not enough arguments!")


@dp.message(Command("rmcl"))
async def rmcl_handler(message: Message):
    if message.from_user.id == 1909320566:
        args = message.text.split(" ")[1:]
        print("rmcl args:", args)
        if len(args) >= 1:
            username = args[0].replace('@', '')
            with ClientsDatabaseConnection() as db:
                client = db.read_clients().by_telegram_username(username)
                if client is not None:
                    db.delete_client(username)
                    await message.reply(f"- {client}")
                else:
                    await message.reply(f"!= any client")
        else:
            await message.reply("Not enough arguments!")

@dp.message(Command("getcl"))
async def getcl_handler(message: Message):
    if message.from_user.id == 1909320566:
        args = message.text.split(" ")[1:]
        print("getcl args:", args)
        if len(args) >= 1:
            username = args[0].replace('@', '')
            with ClientsDatabaseConnection() as db:
                client = db.read_clients().by_telegram_username(username)
                if client is not None:
                    await message.reply(f"== {client}")
                else:
                    await message.reply(f"!= any client")
        else:
            await message.reply("Not enough args")


@dp.message()
async def message_cleaner(message: Message):
    await message.delete()

async def start_bot():
    await send_to_all_clients("Бот запущений!")
    await dp.start_polling(bot)

async def send_to_all_clients(message: str):
    # for chat_id in chat_ids:
    #     await bot.send_message(chat_id, message)
    pass