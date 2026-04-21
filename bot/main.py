from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Config, load_config
from bot.keyboards import main_keyboard
from bot.store import Store


async def run_bot() -> None:
    config: Config = load_config()
    store = Store(config.db_path)

    bot = Bot(config.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: Message) -> None:
        if message.from_user is None:
            return
        store.ensure_user(message.from_user.id)
        text = (
            "🔥 Добро пожаловать в цифровой маркет!\n\n"
            "Здесь можно купить: файлы, фото, игровые аккаунты, донаты и услуги.\n"
            f"Валюта бота: {config.currency_name}.\n"
            f"Курс: 1 {config.currency_name} = {config.rub_per_coin} ₽"
        )
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(Command("catalog"))
    @dp.message(F.text == "🛍 Каталог")
    async def catalog(message: Message) -> None:
        items = store.list_items()
        if not items:
            await message.answer("Пока нет доступных товаров.")
            return

        lines = ["🛍 Каталог:"]
        for item in items:
            lines.append(
                f"\nID: {item.id}\n{item.title} ({item.category})\n"
                f"{item.description}\n"
                f"Цена: {item.price} {config.currency_name} | Остаток: {item.stock}"
            )
        lines.append("\nПокупка: /buy <id>")
        await message.answer("\n".join(lines))

    @dp.message(Command("balance"))
    @dp.message(F.text == "💳 Баланс")
    async def balance(message: Message) -> None:
        if message.from_user is None:
            return
        balance_value = store.get_balance(message.from_user.id)
        await message.answer(f"Ваш баланс: {balance_value} {config.currency_name}")

    @dp.message(Command("topup"))
    @dp.message(F.text == "💎 Пополнить NOVA")
    async def topup(message: Message) -> None:
        parts = (message.text or "").split()
        if len(parts) == 2 and parts[1].isdigit():
            amount = int(parts[1])
            rub = amount * config.rub_per_coin
            await message.answer(
                f"Пополнение {amount} {config.currency_name} = {rub} ₽\n"
                "Оплата вручную через администратора."
            )
        else:
            await message.answer(
                "Формат: /topup <кол-во>\n"
                f"Текущий курс: 1 {config.currency_name} = {config.rub_per_coin} ₽"
            )

    @dp.message(Command("buy"))
    async def buy(message: Message) -> None:
        if message.from_user is None:
            return
        parts = (message.text or "").split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("Формат: /buy <id>")
            return

        item_id = int(parts[1])
        ok, result = store.buy(message.from_user.id, item_id)
        if ok:
            await message.answer(
                "✅ Покупка успешна!\n"
                f"Ваш цифровой товар:\n{result}"
            )
        else:
            await message.answer(f"❌ {result}")

    @dp.message(Command("admin_add_item"))
    async def admin_add_item(message: Message) -> None:
        if message.from_user is None or message.from_user.id not in config.admin_ids:
            await message.answer("Доступ только для админа.")
            return

        template = (
            "Используй формат:\n"
            "/admin_add_item Название|Категория|Описание|Цена NOVA|Остаток|Выдача"
        )

        raw = message.text or ""
        payload = raw.replace("/admin_add_item", "", 1).strip()
        if not payload:
            await message.answer(template)
            return

        parts = payload.split("|")
        if len(parts) != 6 or not parts[3].isdigit() or not parts[4].isdigit():
            await message.answer(template)
            return

        item = store.add_item(
            title=parts[0].strip(),
            category=parts[1].strip(),
            description=parts[2].strip(),
            price=int(parts[3]),
            stock=int(parts[4]),
            payload=parts[5].strip(),
        )
        await message.answer(f"Добавлен товар ID {item.id}: {item.title}")

    @dp.message(Command("admin_add_nova"))
    async def admin_add_nova(message: Message) -> None:
        if message.from_user is None or message.from_user.id not in config.admin_ids:
            await message.answer("Доступ только для админа.")
            return

        parts = (message.text or "").split()
        if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
            await message.answer("Формат: /admin_add_nova <user_id> <amount>")
            return

        target_id = int(parts[1])
        amount = int(parts[2])
        store.add_balance(target_id, amount)
        await message.answer(f"Начислено {amount} {config.currency_name} пользователю {target_id}")

    @dp.message(Command("admin_stock"))
    async def admin_stock(message: Message) -> None:
        if message.from_user is None or message.from_user.id not in config.admin_ids:
            await message.answer("Доступ только для админа.")
            return

        items = store.stock_report()
        if not items:
            await message.answer("Склад пуст.")
            return

        text = "\n\n".join(
            f"ID {item.id}: {item.title}\nОстаток: {item.stock}\nЦена: {item.price} {config.currency_name}"
            for item in items
        )
        await message.answer(text)

    @dp.message(F.text == "ℹ️ Помощь")
    async def help_text(message: Message) -> None:
        await message.answer(
            "Команды:\n"
            "/catalog\n/balance\n/topup <кол-во>\n/buy <id>\n\n"
            "Админ:\n/admin_add_item\n/admin_add_nova\n/admin_stock"
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
