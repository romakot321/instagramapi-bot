from fastapi import APIRouter, Body, Depends

from api.services.user import UserService

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/{telegram_id}/report", include_in_schema=False)
async def user_report_webhook(
    telegram_id: int, username: str = Body(), user_service: UserService = Depends()
):
    await user_service.send_report(telegram_id, username)
