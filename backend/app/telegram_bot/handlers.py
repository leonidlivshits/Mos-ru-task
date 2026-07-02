from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.telegram_bot.backend_client import BackendApiError, BackendClient
from app.telegram_bot.dates import parse_lost_date
from app.telegram_bot.formatting import format_claim_check_result, format_lost_request_result
from app.telegram_bot.keyboards import stations_keyboard
from app.telegram_bot.messages import (
    BACKEND_UNAVAILABLE_MESSAGE,
    CANCEL_MESSAGE,
    CLAIM_FEATURE_REQUIRED_MESSAGE,
    DAMAGED_DATE_MESSAGE,
    DESCRIPTION_REQUIRED_MESSAGE,
    FALLBACK_MESSAGE,
    INVALID_LOST_DATE_MESSAGE,
    LOST_DATE_PROMPT,
    LOST_DATE_REQUIRED_MESSAGE,
    START_MESSAGE,
    STATION_PROMPT,
    claim_check_error_message,
    claim_feature_prompt,
    create_request_error_message,
)
from app.telegram_bot.states import LostItemFlow

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LostItemFlow.description)
    await message.answer(START_MESSAGE)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(CANCEL_MESSAGE)


@router.message(LostItemFlow.description)
async def receive_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(DESCRIPTION_REQUIRED_MESSAGE)
        return

    await state.update_data(description=message.text.strip())
    await state.set_state(LostItemFlow.lost_date)
    await message.answer(LOST_DATE_PROMPT)


@router.message(LostItemFlow.lost_date)
async def receive_lost_date(
    message: Message,
    state: FSMContext,
    backend_client: BackendClient,
) -> None:
    if not message.text:
        await message.answer(LOST_DATE_REQUIRED_MESSAGE)
        return

    lost_date = parse_lost_date(message.text)
    if lost_date is None:
        await message.answer(INVALID_LOST_DATE_MESSAGE)
        return

    try:
        stations = await backend_client.list_stations()
    except BackendApiError:
        await message.answer(BACKEND_UNAVAILABLE_MESSAGE)
        return

    await state.update_data(lost_date=lost_date.isoformat())
    await state.set_state(LostItemFlow.station)
    await message.answer(
        STATION_PROMPT,
        reply_markup=stations_keyboard(stations),
    )


@router.callback_query(LostItemFlow.station, F.data.startswith("station:"))
async def receive_station(
    callback: CallbackQuery,
    state: FSMContext,
    backend_client: BackendClient,
) -> None:
    await callback.answer()

    station_id = int((callback.data or "").split(":", 1)[1])
    data = await state.get_data()
    lost_date = parse_lost_date(data["lost_date"])
    if lost_date is None:
        if callback.message:
            await callback.message.answer(DAMAGED_DATE_MESSAGE)
        await state.clear()
        return

    try:
        result = await backend_client.create_lost_request(
            description=data["description"],
            lost_date=lost_date,
            station_id=station_id,
        )
    except BackendApiError as exc:
        await state.clear()
        if callback.message:
            await callback.message.answer(create_request_error_message(exc))
        return

    if callback.message:
        await callback.message.answer(format_lost_request_result(result))

    if not result.matches:
        await state.clear()
        return

    best_match = result.matches[0]
    await state.update_data(
        request_id=result.request_id,
        claim_item_id=best_match.item_id,
        claim_item_title=best_match.title,
    )
    await state.set_state(LostItemFlow.claim_feature)
    if callback.message:
        await callback.message.answer(claim_feature_prompt(best_match.title))


@router.message(LostItemFlow.claim_feature)
async def receive_claim_feature(
    message: Message,
    state: FSMContext,
    backend_client: BackendClient,
) -> None:
    if not message.text:
        await message.answer(CLAIM_FEATURE_REQUIRED_MESSAGE)
        return

    data = await state.get_data()
    try:
        result = await backend_client.claim_check(
            request_id=data["request_id"],
            found_item_id=data["claim_item_id"],
            answer=message.text.strip(),
        )
    except BackendApiError as exc:
        await state.clear()
        await message.answer(claim_check_error_message(exc))
        return

    await state.clear()
    await message.answer(format_claim_check_result(result))


@router.message()
async def fallback(message: Message) -> None:
    await message.answer(FALLBACK_MESSAGE)
