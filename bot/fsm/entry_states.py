from aiogram.fsm.state import State, StatesGroup

class EntryStates(StatesGroup):
    choosing_type = State()
    choosing_amount = State()
    choosing_category = State()
    choosing_date = State()