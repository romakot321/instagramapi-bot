from fastapi import APIRouter, Body, Depends

from api.services.user import UserService
from api.schemas.user import UserReportSchema

router = APIRouter(prefix="/api/user", tags=["User"])


@router.post("/{telegram_id}/report", include_in_schema=False)
async def user_report_webhook(
    telegram_id: int, schema: UserReportSchema, user_service: UserService = Depends(UserService.depend)
):
    await user_service.send_report(telegram_id, schema)
