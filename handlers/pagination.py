from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from keyboards.inline import pagination_keyboard
from keyboards.default import main_menu
from services.queries import get_tips_paginated, get_paychecks_paginated

router = Router()
ITEMS_PER_PAGE = 10


@router.message(lambda msg: msg.text == "Все типсы")
async def all_tips(message: Message):
    page = 1
    tips, has_next = await get_tips_paginated(message.from_user.id, page, ITEMS_PER_PAGE)

    if not tips:
        await message.answer("Типсов пока нет.", reply_markup=main_menu())
        return

    text = "📋 <b>Список типсов</b>:\n\n" + "\n".join(
        [f"{idx+1}. {tip.date} — {tip.amount}$ — {tip.workplace}" for idx, tip in enumerate(tips)]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("tips", page, has_next))


@router.message(lambda msg: msg.text == "Все пейчеки")
async def all_paychecks(message: Message):
    page = 1
    paychecks, has_next = await get_paychecks_paginated(message.from_user.id, page, ITEMS_PER_PAGE)

    if not paychecks:
        await message.answer("Пейчеков пока нет.", reply_markup=main_menu())
        return

    text = "📋 <b>Список пейчеков</b>:\n\n" + "\n".join(
        [f"{idx+1}. {p.date} — {p.amount}$ — {p.workplace}" for idx, p in enumerate(paychecks)]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=pagination_keyboard("paychecks", page, has_next))


@router.callback_query(lambda c: c.data.startswith("tips_page:"))
async def tips_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    tips, has_next = await get_tips_paginated(callback.from_user.id, page, ITEMS_PER_PAGE)

    text = f"📋 <b>Типсы (стр. {page})</b>\n\n" + "\n".join([
        f"{t.date} - {t.amount} $ ({t.workplace})" for t in tips
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("tips", page, has_next))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("paychecks_page:"))
async def paychecks_page_callback(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])
    paychecks, has_next = await get_paychecks_paginated(callback.from_user.id, page, ITEMS_PER_PAGE)

    text = f"📋 <b>Пейчеки (стр. {page})</b>\n\n" + "\n".join([
        f"{p.date} - {p.amount} $ ({p.workplace})" for p in paychecks
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=pagination_keyboard("paychecks", page, has_next))
    await callback.answer()
