from aiogram.fsm.state import StatesGroup, State

'''class IncomeStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    confirm = State()
    

class ExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    confirm = State()'''

class StatisticsStates(StatesGroup):
    waiting_for_period = State()
    waiting_for_category = State()

class CustomStatsStates(StatesGroup):
    choosing_start_date = State()
    choosing_end_date = State()

class EntryStates(StatesGroup):
    choosing_type = State()       # доход или расход
    choosing_amount = State()
    choosing_category = State()
    choosing_date = State()       # выбор даты (сегодня / календарь)
    confirming = State()

class AnalysisStates(StatesGroup):
    waiting_for_continue = State()
    in_progress = State()

class ReceiptStates(StatesGroup):
    waiting_for_photo_or_document = State()
    waiting_for_user_confirm = State()




