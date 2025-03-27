from aiogram.fsm.state import State, StatesGroup


class TrackingCreateForm(StatesGroup):
    typing_username = State()

