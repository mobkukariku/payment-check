from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from fsm.tip_fsm import TipFSM
from keyboards.default import workplace_keyboard, main_menu
from services.queries import add_tip

router = Router()


@router.message(lambda msg: msg.text == "Добавить типсы")
async def start_tip(message: types.Message, state: FSMContext):
    await state.set_state(TipFSM.date)
    await message.answer("📅 Введи дату (например: 2024-06-29)")

@router.message(TipFSM.date)
async def tip_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(TipFSM.amount)
    await message.answer("💰 Введи сумму чаевых (например: 180)")

@router.message(TipFSM.amount)
async def tip_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("❌ Введи корректную сумму")
        return

    await state.set_state(TipFSM.workplace)
    await message.answer("🏢 Выбери место работы:", reply_markup=workplace_keyboard())

@router.message(TipFSM.workplace)
async def tip_workplace(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_tip(
        user_id=message.from_user.id,
        date=data["date"],
        amount=data["amount"],
        workplace=message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Типсы добавлены!", reply_markup=main_menu())