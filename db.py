from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, text, select, BigInteger
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)  # Telegram user ID
    date = Column(String)
    amount = Column(Float)
    workplace = Column(String)

class Paycheck(Base):
    __tablename__ = "paychecks"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    date = Column(String)
    amount = Column(Float)
    workplace = Column(String)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



async def add_tip(user_id, date, amount, workplace):
    async with async_session() as session:
        session.add(Tip(user_id=user_id, date=date, amount=amount, workplace=workplace))
        await session.commit()

async def add_paycheck(user_id, date, amount, workplace):
    async with async_session() as session:
        session.add(Paycheck(user_id=user_id, date=date, amount=amount, workplace=workplace))
        await session.commit()


async def get_statistics(user_id: int):
    async with async_session() as session:
        tips_sum = await session.scalar(text("SELECT SUM(amount) FROM tips WHERE user_id = :uid"), {"uid": user_id})
        paychecks_sum = await session.scalar(text("SELECT SUM(amount) FROM paychecks WHERE user_id = :uid"), {"uid": user_id})

        max_tip = await session.scalar(
            select(Tip).where(Tip.user_id == user_id).order_by(Tip.amount.desc()).limit(1)
        )
        max_paycheck = await session.scalar(
            select(Paycheck).where(Paycheck.user_id == user_id).order_by(Paycheck.amount.desc()).limit(1)
        )

        return {
            "tips_sum": tips_sum or 0,
            "paychecks_sum": paychecks_sum or 0,
            "max_tip": max_tip,
            "max_paycheck": max_paycheck
        }

async def get_tips_paginated(user_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT date, amount, workplace
            FROM tips
            WHERE user_id = :uid
            ORDER BY date DESC
            LIMIT :limit OFFSET :offset
        """), {"uid": user_id, "limit": limit + 1, "offset": offset})
        rows = result.fetchall()
        has_next = len(rows) > limit
        return rows[:limit], has_next


async def get_paychecks_paginated(user_id: int, page: int, limit: int):
    offset = (page - 1) * limit
    async with async_session() as session:
        result = await session.execute(text("""
            SELECT date, amount, workplace
            FROM paychecks
            WHERE user_id = :uid
            ORDER BY date DESC
            LIMIT :limit OFFSET :offset
        """), {"uid": user_id, "limit": limit + 1, "offset": offset})
        rows = result.fetchall()
        has_next = len(rows) > limit
        return rows[:limit], has_next