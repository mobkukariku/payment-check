from aiogram.fsm.state import State, StatesGroup

class TipFSM(StatesGroup):
    date = State()
    amount = State()
    workplace = State()
