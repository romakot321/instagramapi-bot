import os
from aiohttp import ClientSession
from fastapi import HTTPException


class CloudpaymentsRepository:
    api_url = "https://api.cloudpayments.ru"
    api_public_id = os.getenv("CLOUDPAYMENTS_API_PUBLIC_ID")
    api_secret_key = os.getenv("CLOUDPAYMENTS_API_TOKEN")

    async def cancel_subscription_renewal(self, subscription_id: str) -> bool:
        async with ClientSession(base_url=self.api_url, headers={"Content-Type": "application/json"}) as session:
            resp = await session.post("/subcriptions/cancel", json={"Id": subscription_id})
            if resp.status != 200:
                raise HTTPException(500)
            body = await resp.json()
            return body.get("Success") == True
        return False
