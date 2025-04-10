import os
import hashlib
import hmac
import base64
import json
import humanize
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from api.services.subscription import SubscriptionService

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="templates")

templates.env.filters["humanize_seconds"] = lambda i: humanize.naturaldelta(dt.timedelta(seconds=i))


@router.get("/paywall", response_class=HTMLResponse)
async def paywall(
        request: Request,
        tracking_username: str | None = Query(None),
        tariff_id: int | None = Query(None),
        service: SubscriptionService = Depends(SubscriptionService.depend)
):
    tariffs = await service.get_tariffs_list()
    if tariff_id is not None:
        tariffs = [t for t in tariffs if t.id == tariff_id]
    return templates.TemplateResponse(
        "paywall.html",
        {
            "request": request,
            "tariffs": tariffs,
            "tracking_username": tracking_username
        }
    )


@router.get("/paywall/bigTracking", response_class=HTMLResponse)
async def paywall_big_tracking(
        request: Request,
        username: str = Query(),
        service: SubscriptionService = Depends(SubscriptionService.depend)
):
    tariffs = await service.get_tariffs_big_tracking_list()
    return templates.TemplateResponse(
        "paywall_big_tracking.html",
        {
            "request": request,
            "tariffs": tariffs,
            "tracking_username": username
        }
    )

