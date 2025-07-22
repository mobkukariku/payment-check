import os

import openai
from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from fsm.chatgpt_fsm import ChatGPTFSM
from keyboards.default import main_menu, back_keyboard

openai.api_key = os.getenv("OPENAI_API_KEY")
router = Router()

@router.message(lambda msg: msg.text == "Помощник")
async def start_gpt(message: types.Message, state: FSMContext):
    await message.answer("Привет я ии помощник отвечу на любой твой вопрос!", reply_markup=back_keyboard())
    await state.set_state(ChatGPTFSM.waiting_for_prompt)


@router.message(ChatGPTFSM.waiting_for_prompt)
async def prompt_gpt(message: Message, state: FSMContext):
    user_prompt = message.text

    if user_prompt == "⬅️ Назад":  # или что у тебя в кнопке
        await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu())
        await state.clear()
        return

    await message.answer("🔄 Думаю...")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты финансовый ассистент по имени Орочимару. "
                        "Тебя создал самый крутой студент СДУ — Дамир Таганхожаев, студент 3 курса, лучший ксник и просто соска 😎. "
                        "Отвечай профессионально, кратко и по делу. "
                        "Помогай пользователям управлять личными финансами, зарплатами и бюджетами."
                    )
                },
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")

    # НЕ очищаем состояние, чтобы пользователь мог писать дальше
