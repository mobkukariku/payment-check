from aiogram.fsm.state import State, StatesGroup

class ChatGPTFSM(StatesGroup):
    waiting_for_prompt = State()