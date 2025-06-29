import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, SECRET_MESSAGE
from db import init_db, add_tip, add_paycheck, get_statistics, get_paychecks_paginated, get_tips_paginated

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ITEMS_PER_PAGE = 10


class TipFSM(StatesGroup):
    date = State()
    amount = State()
    workplace = State()


class PaycheckFSM(StatesGroup):
    date = State()
    amount = State()
    workplace = State()

def pagination_keyboard(entity: str, page: int, has_next: bool):
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{entity}_page:{page-1}"))
    if has_next:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"{entity}_page:{page+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить типсы")],
            [KeyboardButton(text="Добавить пейчек")],
            [KeyboardButton(text="Статистика")],
            [KeyboardButton(text="Все типсы"), KeyboardButton(text="Все пейчеки")],
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Что хочешь сделать?", reply_markup=main_menu())


# === TIPS ===
@dp.message(lambda msg: msg.text == "Добавить типсы")
async def handle_add_tip(message: types.Message, state: FSMContext):
    await state.set_state(TipFSM.date)
    await message.answer("📅 Введи дату (например: 2024-06-29)")


@dp.message(TipFSM.date)
async def handle_tip_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(TipFSM.amount)
    await message.answer("💰 Введи сумму чаевых (например: 180)")


@dp.message(TipFSM.amount)
async def handle_tip_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("❌ Введи корректную сумму (например: 150)")
        return

    await state.set_state(TipFSM.workplace)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Работа 1")],
            [KeyboardButton(text="Работа 2")],
            [KeyboardButton(text="Работа 3")],
        ],
        resize_keyboard=True
    )
    await message.answer("🏢 Выбери место работы:", reply_markup=kb)


@dp.message(TipFSM.workplace)
async def handle_tip_workplace(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_tip(
        user_id=message.from_user.id,
        date=data['date'],
        amount=data['amount'],
        workplace=message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Типсы добавлены! Можешь продолжать.", reply_markup=main_menu())


# === PAYCHECK ===
@dp.message(lambda msg: msg.text == "Добавить пейчек")
async def handle_add_paycheck(message: types.Message, state: FSMContext):
    await state.set_state(PaycheckFSM.date)
    await message.answer("📅 Введи дату пейчека (например: 2024-06-29)")


@dp.message(PaycheckFSM.date)
async def handle_paycheck_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(PaycheckFSM.amount)
    await message.answer("💸 Введи сумму пейчека (например: 800)")


@dp.message(PaycheckFSM.amount)
async def handle_paycheck_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("❌ Введи корректную сумму (например: 800)")
        return

    await state.set_state(PaycheckFSM.workplace)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Работа 1")],
            [KeyboardButton(text="Работа 2")],
            [KeyboardButton(text="Работа 3")],
        ],
        resize_keyboard=True
    )
    await message.answer("🏢 Выбери место работы:", reply_markup=kb)


@dp.message(PaycheckFSM.workplace)
async def handle_paycheck_workplace(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_paycheck(
        user_id=message.from_user.id,
        date=data['date'],
        amount=data['amount'],
        workplace=message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Пейчек добавлен!", reply_markup=main_menu())


# === STATISTICS ===
@dp.message(lambda msg: msg.text == "Статистика")
async def handle_stats(message: types.Message):
    data = await get_statistics(user_id=message.from_user.id)

    total = data["tips_sum"] + data["paychecks_sum"]

    # 📊 Таблица статистики
    stat_table = (
        "📊 <b>Статистика</b>\n"
        "<pre>"
        "┌────────────────┬────────────┐\n"
        f"│ Тип            │ Сумма ($) │\n"
        "├────────────────┼────────────┤\n"
        f"│ Типсы          │ {int(data['tips_sum']):>10,} │\n"
        f"│ Пейчеки        │ {int(data['paychecks_sum']):>10,} │\n"
        f"│ Итого          │ {int(total):>10,} │\n"
        "└────────────────┴────────────┘\n"
        "</pre>"
    )

    # 🔝 Самые большие записи
    max_tip = data["max_tip"]
    max_paycheck = data["max_paycheck"]

    max_info = ""
    if max_tip:
        max_info += (
            f"\n🔝 <b>Самый большой типс</b>: {int(max_tip.amount):,} $\n"
            f"🏢 Место: {max_tip.workplace}\n"
            f"📅 Дата: {max_tip.date}\n"
        )
    if max_paycheck:
        max_info += (
            f"\n🔝 <b>Самый большой пейчек</b>: {int(max_paycheck.amount):,} $\n"
            f"🏢 Место: {max_paycheck.workplace}\n"
            f"📅 Дата: {max_paycheck.date}\n"
        )

    await message.answer(stat_table + max_info, parse_mode="HTML")


@dp.message(lambda msg: msg.text == "Все типсы")
async def all_tips(message: Message):
    page = 1
    tips, has_next = await get_tips_paginated(message.from_user.id, page, ITEMS_PER_PAGE)

    if not tips:
        await message.answer("Типсов пока нет.", reply_markup=main_menu())
        return

    text = "📋 <b>Список типсов</b>:\n\n" + "\n".join(
        [f"{idx+1}. {tip.date} — {tip.amount}$ — {tip.workplace}" for idx, tip in enumerate(tips)]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("tip", page, has_next))


@dp.message(lambda msg: msg.text == "Все пейчеки")
async def all_paychecks(message: Message):
    page = 1
    paychecks, has_next = await get_paychecks_paginated(message.from_user.id ,page, ITEMS_PER_PAGE)

    if not paychecks:
        await message.answer("Пейчеков пока нет.", reply_markup=main_menu())
        return

    text = "📋 <b>Список пейчеков</b>:\n\n" + "\n".join(
        [f"{idx+1}. {p.date} — {p.amount}$ — {p.workplace}" for idx, p in enumerate(paychecks)]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("paycheck", page, has_next))


@dp.callback_query(lambda c: c.data.startswith("tip_page:"))
async def tip_pagination(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    tips, has_next = await get_tips_paginated(callback.from_user.id, page, ITEMS_PER_PAGE)

    text = "📋 <b>Список типсов</b>:\n\n" + "\n".join(
        [f"{idx+1}. {tip.date} — {tip.amount}$ — {tip.workplace}" for idx, tip in enumerate(tips)]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("tip", page, has_next))


@dp.callback_query(lambda c: c.data.startswith("paycheck_page:"))
async def paycheck_pagination(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    paychecks, has_next = await get_paychecks_paginated(callback.from_user.id ,page, ITEMS_PER_PAGE)

    text = "📋 <b>Список пейчеков</b>:\n\n" + "\n".join(
        [f"{idx+1}. {p.date} — {p.amount}$ — {p.workplace}" for idx, p in enumerate(paychecks)]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("paycheck", page, has_next))

@dp.message(lambda msg: msg.text == "Все типсы")
async def all_tips(message: types.Message):
    page = 1
    tips, has_next = await get_tips_paginated(message.from_user.id , page=page, limit=ITEMS_PER_PAGE)
    text = "📋 <b>Типсы (стр. 1)</b>\n\n" + "\n".join([
        f"{t.date} - {t.amount} $ ({t.workplace})" for t in tips
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("tips", page, has_next))


@dp.message(lambda msg: msg.text == "Все пейчеки")
async def all_paychecks(message: types.Message):
    page = 1
    paychecks, has_next = await get_paychecks_paginated(message.from_user.id, page=page, limit=ITEMS_PER_PAGE)
    text = "📋 <b>Пейчеки (стр. 1)</b>\n\n" + "\n".join([
        f"{p.date} - {p.amount} $ ({p.workplace})" for p in paychecks
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("paychecks", page, has_next))


@dp.callback_query(lambda c: c.data.startswith("tips_page:"))
async def tips_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    tips, has_next = await get_tips_paginated(callback.from_user.id ,page=page, limit=ITEMS_PER_PAGE)
    text = f"📋 <b>Типсы (стр. {page})</b>\n\n" + "\n".join([
        f"{t.date} - {t.amount} $ ({t.workplace})" for t in tips
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("tips", page, has_next))
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("paychecks_page:"))
async def paychecks_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    paychecks, has_next = await get_paychecks_paginated(callback.from_user.id ,page=page, limit=ITEMS_PER_PAGE)
    text = f"📋 <b>Пейчеки (стр. {page})</b>\n\n" + "\n".join([
        f"{p.date} - {p.amount} $ ({p.workplace})" for p in paychecks
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("paychecks", page, has_next))
    await callback.answer()

@dp.message(lambda msg: msg.text == "привет")
async def handle_hello(message: types.Message):
    await message.answer(
        "Привет",
    )

@dp.message(lambda msg: msg.text == "ilu")
async def handle_ilu(message: types.Message):
    await message.answer(
        SECRET_MESSAGE
    )

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
