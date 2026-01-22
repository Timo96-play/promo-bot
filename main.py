import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(TOKEN)
dp = Dispatcher()

reply_to_user = {}

def reply_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✉️ Ответить пользователю",
                callback_data=f"reply:{user_id}"
            )]
        ]
    )

@dp.message()
async def forward_to_admin(msg: Message):
    if msg.from_user.id == ADMIN_ID:
        return

    await bot.send_message(
        ADMIN_ID,
        f"📩 Сообщение от пользователя\n"
        f"ID: {msg.from_user.id}\n\n"
        f"{msg.text}",
        reply_markup=reply_keyboard(msg.from_user.id)
    )

@dp.callback_query(F.data.startswith("reply:"))
async def choose_user(callback):
    user_id = int(callback.data.split(":")[1])
    reply_to_user[callback.from_user.id] = user_id
    await callback.message.answer("✍️ Напиши ответ — я отправлю его пользователю")
    await callback.answer()

@dp.message(F.from_user.id == ADMIN_ID)
async def send_reply(msg: Message):
    user_id = reply_to_user.get(msg.from_user.id)
    if not user_id:
        return

    await bot.send_message(user_id, msg.text)
    await msg.answer("✅ Отправлено")
    reply_to_user.pop(msg.from_user.id, None)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
