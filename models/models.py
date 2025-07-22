from sqlalchemy import Column, Integer, String, Float, BigInteger
from services.database import Base

class Tip(Base):
    __tablename__ = "tips"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
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


