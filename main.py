import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import LabeledPrice, PreCheckoutQuery

TOKEN = "9206225712:AAFDYmU2kilBc0OLYKLG7vZMPye4MNc-E7Y"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

LEVELS = {
    "lvl_1": {
        "name": "Level 1: Старт",
        "price_stars": 35,
        "description": "💡 Бюджетные предметы для новичков (до $5). Минимальный порог входа, стабильный рост.",
        "items": [
            "• AK-47 | Сланец (Прямо с завода) — Покупать при просадке на 4%, продавать через 2 недели.",
            "• M4A4 | Репост (После полевых) — Ждать роста во время патча."
        ]
    },
    "lvl_2": {
        "name": "Level 2: Уверенный",
        "price_stars": 59,
        "description": "📈 Предметы средней ценовой категории ($5 - $15). Анализ ликвидности и объемов.",
        "items": [
            "• USP-S | Извилины (Прямо с завода) — Высокий спрос перед мейджорами.",
            "• AWP | Ахерон (Поношенное) — Цикличный рост на выходных."
        ]
    },
    "lvl_3": {
        "name": "Level 3: Профи",
        "price_stars": 199,
        "description": "🔥 Дорогие скины ($15 - $40) с глубоким фундаментальным анализом и прогнозом ожидания.",
        "items": [
            "• Desert Eagle | Пламя (После полевых) — Дефицит на торговой площадке, держать 30 дней.",
            "• Перчатки | Спектр (Закаленное в боях) — Инвестиция с максимальной маржинальностью."
        ]
    },
    "lvl_4": {
        "name": "Level 4: Инвестор",
        "price_stars": 399,
        "description": "💎 Премиальный уровень ($40 - $100). Редкие паттерны и наклейки.",
        "items": [
            "• Нож-боя | Лесной дамасск — Ожидание роста +25% за счет сокращения выпадения кейсов.",
            "• Акция на капсулы Kato 2019 — Долгосрок (от 3 месяцев)."
        ]
    },
    "lvl_5": {
        "name": "Level 5: Кирпич (VIP)",
        "price_stars": 799,
        "description": "👑 Закрытый инсайдерский пул ($100+). Топовые ножи и перчатки с гарантией аналитики ska322.",
        "items": [
            "• Керамбит | Кровавая паутина — Точечный закуп на падении рынка, фиксация на пике.",
            "• Бабочка | Водная струя — Анализ китов рынка, прогноз точной даты продажи."
        ]
    },
}

def get_main_menu():
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📊 Каталог уровней аналитики", callback_data="catalog")],
            [types.InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile"), 
             types.InlineKeyboardButton(text="ℹ️ О проекте ska322", callback_data="about")],
            [types.InlineKeyboardButton(text="📢 Наш Telegram канал", url="https://t.me/ska322")]
        ]
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        f"👋 Привет, **{message.from_user.first_name}**!\n\n"
        "Добро пожаловать в официальный бот аналитики предметов CS2 от канала **ska322** 📉📈\n\n"
        "Здесь вы получаете:\n"
        "• Точное время закупа и продажи скинов\n"
        "• Глубокую аналитику рынка на основе алгоритмов\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu())

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Главное меню аналитики **ska322** 👇",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "catalog")
async def cb_catalog(callback: types.CallbackQuery):
    buttons = []
    for key, lvl in LEVELS.items():
        buttons.append([
            types.InlineKeyboardButton(
                text=f"{lvl['name']} — ⭐ {lvl['price_stars']} Telegram Stars",
                callback_data=f"buy_{key}"
            )
        ])
    buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "🛒 **Выберите уровень аналитики:**\n\n"
        "Чем выше уровень, тем ценнее инсайды и точнее прогнозы роста активов.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def cb_buy(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    lvl_key = f"{parts[1]}_{parts[2]}"
    lvl_data = LEVELS.get(lvl_key)
    
    if not lvl_data:
        await callback.answer("Уровень не найден!", show_alert=True)
        return

    prices = [LabeledPrice(label=lvl_data["name"], amount=lvl_data["price_stars"])]
    
    await callback.message.answer_invoice(
        title=lvl_data["name"],
        description=f"Доступ к аналитике: {lvl_data['description']}",
        payload=f"sub_{lvl_key}",
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    lvl_key = payload.replace("sub_", "")
    lvl_data = LEVELS.get(lvl_key)
    
    if not lvl_data:
        return

    items_text = "\n".join(lvl_data["items"])
    
    await message.answer(
        f"✅ **Оплата прошла успешно! Спасибо за покупку в ska322!** 🎉\n\n"
        f"📊 **Ваша аналитика для {lvl_data['name']}:**\n"
        f"{lvl_data['description']}\n\n"
        f"🔫 **Рекомендации к покупке:**\n{items_text}\n\n"
        f"⏳ *Следите за обновлениями рынка в канале!*",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ В главное меню", callback_data="main_menu")]]
        )
    )

@dp.callback_query(F.data == "profile")
async def cb_profile(callback: types.CallbackQuery):
    user = callback.message.from_user
    await callback.message.edit_text(
        f"👤 **Ваш профиль:**\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Имя: {user.first_name}\n\n"
        f"Здесь отображается статус ваших подписок на аналитику.",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]]
        )
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def cb_about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **О проекте ska322**\n\n"
        "Профессиональная аналитика рынка Counter-Strike 2. "
        "Сигналы на покупку и продажу скинов с глубокой проработкой.\n\n"
        "Официальный канал: @ska322",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]]
        )
    )
    await callback.answer()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
aiogram==3.13.1
