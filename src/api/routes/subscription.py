from fastapi import APIRouter, Depends

from api.schemas.subscription import SubscriptionAddRequestsSchema, SubscriptionBigTrackingCreateSchema, SubscriptionCreateSchema
from api.services.subscription import SubscriptionService
from api.services.tracking import TrackingService

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.post("")
async def create_subscription(
    schema: SubscriptionCreateSchema,
    service: SubscriptionService = Depends(SubscriptionService.depend),
    tracking_service: TrackingService = Depends(TrackingService.depend)
):
    if schema.tracking_username:
        await tracking_service.create(schema.user_telegram_id, schema.tracking_username)
    return await service.create(schema)


@router.post("/requests")
async def add_subscription_requests(
    schema: SubscriptionAddRequestsSchema,
    service: SubscriptionService = Depends(SubscriptionService.depend),
):
    return await service.add_requests(schema)


@router.post("/bigTracking")
async def create_subscription_big_tracking(
    schema: SubscriptionBigTrackingCreateSchema,
    service: SubscriptionService = Depends(SubscriptionService.depend),
    tracking_service: TrackingService = Depends(TrackingService.depend)
):
    await tracking_service.create(schema.user_telegram_id, schema.tracking_username)
    return await service.create(schema)
