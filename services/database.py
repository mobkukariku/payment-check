from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    from models.models import Tip, Paycheck
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
