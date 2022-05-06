from aiogram.dispatcher.fsm.state import StatesGroup, State


class SearchPeople(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    SendPhoto = State()
    EnterFeedbackAddress = State()


class GetMedicine(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    EnterPrescription = State()


class GetProvision(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    ChooseType = State()


class Evacuate(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    EnterSpecialConditions = State()
