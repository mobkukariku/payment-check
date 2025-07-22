from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from fsm.paycheck_fsm import PaycheckFSM
from keyboards.default import workplace_keyboard, main_menu
from services.queries import add_paycheck

router = Router()

@router.message(lambda msg: msg.text == "Добавить пейчек")
async def handle_add_paycheck(message: types.Message, state: FSMContext):
    await state.set_state(PaycheckFSM.date)
    await message.answer("📅 Введи дату пейчека (например: 2024-06-29)")

@router.message(PaycheckFSM.date)
async def handle_paycheck_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(PaycheckFSM.amount)
    await message.answer("💸 Введи сумму пейчека (например: 800)")

@router.message(PaycheckFSM.amount)
async def handle_paycheck_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("❌ Введи корректную сумму (например: 800)")
        return

    await state.set_state(PaycheckFSM.workplace)
    await message.answer("🏢 Выбери место работы:", reply_markup=workplace_keyboard())

@router.message(PaycheckFSM.workplace)
async def handle_paycheck_workplace(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_paycheck(
        user_id=message.from_user.id,
        date=data["date"],
        amount=data["amount"],
        workplace=message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Пейчек добавлен!", reply_markup=main_menu())
