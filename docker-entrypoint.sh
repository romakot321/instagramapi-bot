#!/bin/bash
cd lib/python3.13/site-packages/db && alembic -c alembic.prod.ini upgrade head && cd /app
gunicorn api.main:fastapi_app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 --forwarded-allow-ips="*"
