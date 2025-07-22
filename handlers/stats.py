from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.default import statistics_keyboard, main_menu
from services.generate_plot import generate_tip_plot
from services.queries import get_statistics

router = Router()

@router.message(lambda msg: msg.text == "Статистика")
async def handle_stats(message: types.Message):
    data = await get_statistics(user_id=message.from_user.id)

    total = data["tips_sum"] + data["paychecks_sum"]

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

    await message.answer(stat_table + max_info, parse_mode="HTML", reply_markup=statistics_keyboard())



@router.message(lambda msg: msg.text == "Показать график")
async def handle_income_graph(message: types.Message):
    await message.answer(
        "Еще в разработке",
        reply_markup=main_menu()
    )


@router.message(lambda msg: msg.text == "<- Назад")
async def handle_stats_back(message: types.Message):
    await message.answer(
        text="Вы вернулись в главное меню.",
        reply_markup=main_menu()
    )