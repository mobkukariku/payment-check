from aiogram.fsm.state import State, StatesGroup


class PaycheckFSM(StatesGroup):
    date = State()
    amount = State()
    workplace = State()