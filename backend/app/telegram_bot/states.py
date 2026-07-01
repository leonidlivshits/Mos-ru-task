from aiogram.fsm.state import State, StatesGroup


class LostItemFlow(StatesGroup):
    description = State()
    lost_date = State()
    station = State()
    claim_feature = State()
