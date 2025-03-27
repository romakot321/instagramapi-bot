#!/bin/bash
gunicorn api.main:fastapi_app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 --forwarded-allow-ips="*"
