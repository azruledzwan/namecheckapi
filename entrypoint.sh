#!/bin/sh
. /opt/venv/bin/activate && exec uvicorn main:app --host=0.0.0.0 --port=8000