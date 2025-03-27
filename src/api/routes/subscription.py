from fastapi import APIRouter, Depends

from api.schemas.subscription import SubscriptionCreateSchema
from api.services.subscription import SubscriptionService

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.post("")
async def create_subscription(
    schema: SubscriptionCreateSchema,
    service: SubscriptionService = Depends(SubscriptionService.depend),
):
    return await service.create(schema)
