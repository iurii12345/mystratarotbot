from aiogram.fsm.state import State, StatesGroup

class SpreadStates(StatesGroup):
    waiting_for_question = State()
    question_skipped = State()