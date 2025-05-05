from fastapi import APIRouter, Depends, Body

from api.schemas.payment import PaymentProduct
from api.schemas.subscription import (
    SubscriptionAddRequestsSchema,
    SubscriptionBigTrackingCreateSchema,
    SubscriptionCreateSchema,
)
from api.schemas.payment import PaymentProduct, PaymentSchema
from api.services.payment import PaymentService
from api.services.subscription import SubscriptionService
from api.services.tracking import TrackingService

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


@router.post(
    "", dependencies=[Depends(SubscriptionService.authorize_cloudpayments_webhook)]
)
async def create_subscription(
    schema: PaymentSchema,
    service: SubscriptionService = Depends(SubscriptionService.depend),
    tracking_service: TrackingService = Depends(TrackingService.depend),
    payment_service: PaymentService = Depends(PaymentService.depend),
):
    if schema.data is None or schema.subscription_id is None:
        return {"code": 13}

    tariff = await service.get_tariff(schema.data.tariff_id)
    if tariff.payment_amount != int(schema.amount):
        return {"code": 12}

    if schema.data.product == PaymentProduct.subscription_renewal:
        if schema.data.tracking_username:
            await tracking_service.create(
                schema.data.user_telegram_id, schema.data.tracking_username
            )
        await service.create(
            SubscriptionCreateSchema.model_validate(schema.data.model_dump()),
            schema.subscription_id,
        )
        await payment_service.create(
            schema.data.user_telegram_id,
            schema.transaction_id,
            schema.data.product,
            schema.amount,
            schema.subscription_id,
        )
    elif schema.data.product == PaymentProduct.requests_add:
        await service.add_requests(
            SubscriptionAddRequestsSchema.model_validate(schema.data.model_dump())
        )
        await payment_service.create(
            schema.data.user_telegram_id,
            schema.transaction_id,
            schema.data.product,
            schema.amount,
        )

    return {"code": 0}


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
    tracking_service: TrackingService = Depends(TrackingService.depend),
):
    await tracking_service.create(schema.user_telegram_id, schema.tracking_username)
    return await service.create(schema)
