#!/bin/bash
python -m playwright install chromium --with-deps
uvicorn main:app --host 0.0.0.0 --port 8080
