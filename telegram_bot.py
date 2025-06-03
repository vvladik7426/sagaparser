import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup

api_token = "7582392341:AAEegcVYFVfBHFAMXVj6eC0o1h893TTBjSs"

bot = Bot(api_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

chat_ids: list[int] = []

if os.path.exists("chatIDS"):
    with open("chatIDS", "r") as stream:
        chat_ids.extend([int(_id) for _id in stream.read().split("\n")])

@dp.message(CommandStart())
async def start_handler(message: Message):
    global chat_ids
    if not (message.chat.id in chat_ids):
        chat_ids.append(message.chat.id)
        with open("chatIDS", "w") as stream:
            stream.write("\n".join([str(_id) for _id in chat_ids]))
        await message.delete()
        await message.answer("Вас приєднано до моніторингу.")
    else:
        await message.delete()
        await message.answer("Ви вже приєднані!і")

@dp.message()
async def message_cleaner(message: Message):
    await message.delete()

async def start_bot():
    await send_to_all_clients("Бот запущений!")
    await dp.start_polling(bot)

async def send_to_all_clients(message: str):
    global chat_ids
    for chat_id in chat_ids:
        await bot.send_message(chat_id, message)