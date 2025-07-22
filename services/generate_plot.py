import matplotlib.pyplot as plt
from io import BytesIO
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from db import Tip  # твоя модель

async def generate_tip_plot(user_id: int, session: AsyncSession) -> BytesIO:
    # Достаем данные
    result = await session.execute(
        select(Tip).where(Tip.user_id == user_id)
    )
    tips = result.scalars().all()

    if not tips:
        return None

    # Подготовка данных
    tips.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"))
    dates = [datetime.strptime(t.date, "%Y-%m-%d") for t in tips]
    amounts = [t.amount for t in tips]

    # Построение графика
    plt.figure(figsize=(8, 4))
    plt.plot(dates, amounts, marker='o')
    plt.title("График чаевых")
    plt.xlabel("Дата")
    plt.ylabel("Сумма")
    plt.grid(True)

    # Сохраняем график в байты
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf
