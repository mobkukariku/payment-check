from aiogram import Router, types
from aiogram.filters import Command
from keyboards.default import main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Что хочешь сделать?", reply_markup=main_menu())
