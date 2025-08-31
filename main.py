
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Простий каталог
catalog = [
    {"id": 1, "name": "Вудилище CarpX", "price": 1299, "desc": "Легке і міцне"},
    {"id": 2, "name": "Котушка Daiwa", "price": 2499, "desc": "Японська якість"},
    {"id": 3, "name": "Гачки Owner 10шт", "price": 149, "desc": "Супер гострі"},
]

user_carts = {}

def main_menu():
    kb = [
        [KeyboardButton(text="📦 Каталог")],
        [KeyboardButton(text="🛒 Мій кошик")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! 👋 Це бот-магазин риболовних снастей.
Оберіть дію:", reply_markup=main_menu())

@dp.message(lambda message: message.text == "📦 Каталог")
async def show_catalog(message: types.Message):
    text = "🎣 Наш каталог:

"
    for item in catalog:
        text += f"{item['id']}. {item['name']} — {item['price']} грн
{item['desc']}

"
    text += "Відправ номер товару, щоб додати його в кошик."
    await message.answer(text)

@dp.message(lambda message: message.text.isdigit() and int(message.text) in [item["id"] for item in catalog])
async def add_to_cart(message: types.Message):
    user_id = message.from_user.id
    product_id = int(message.text)
    product = next((item for item in catalog if item["id"] == product_id), None)
    if not product:
        return await message.answer("❌ Товар не знайдено.")

    if user_id not in user_carts:
        user_carts[user_id] = []

    user_carts[user_id].append(product)
    await message.answer(f"✅ {product['name']} додано в кошик!")

@dp.message(lambda message: message.text == "🛒 Мій кошик")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        return await message.answer("🛒 Ваш кошик порожній.")
    text = "🛍 Ваш кошик:

"
    total = 0
    for item in cart:
        text += f"- {item['name']} — {item['price']} грн
"
        total += item['price']
    text += f"
💰 Всього: {total} грн

Відправте 'Замовити', щоб оформити."
    await message.answer(text)

@dp.message(lambda message: message.text.lower() == "замовити")
async def make_order(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        return await message.answer("❌ Кошик порожній.")
    total = sum(item['price'] for item in cart)
    products = ", ".join([item['name'] for item in cart])

    await bot.send_message(ADMIN_ID, f"🆕 Замовлення!

Користувач: @{message.from_user.username}
"
                                    f"ID: {user_id}
"
                                    f"Товари: {products}
"
                                    f"Сума: {total} грн")
    await message.answer("✅ Замовлення оформлено! Чекайте на відповідь адміністратора.")
    user_carts[user_id] = []

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
