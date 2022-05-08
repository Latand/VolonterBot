from aiogram.dispatcher.fsm.state import StatesGroup, State


class SearchPeople(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    SendPhoto = State()
    EnterFeedbackAddress = State()
    EnterAdditionalMessage = State()


class GetMedicine(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    EnterPrescription = State()
    EnterAdditionalMessage = State()


class GetProvision(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    ChooseType = State()
    EnterAdditionalMessage = State()


class Evacuate(StatesGroup):
    EnterAddress = State()
    EnterFullName = State()
    EnterSpecialConditions = State()
    EnterAdditionalMessage = State()
