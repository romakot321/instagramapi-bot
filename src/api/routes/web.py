import os
import hashlib
import hmac
import base64
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from api.services.subscription import SubscriptionService

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="templates")


@router.get("/paywall", response_class=HTMLResponse)
async def paywall(
        request: Request,
        service: SubscriptionService = Depends(SubscriptionService.depend)
):
    tariffs = await service.get_tariffs_list()
    return templates.TemplateResponse(
        "paywall.html",
        {
            "request": request,
            "tariffs": tariffs,
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

