#!/usr/bin/env bash
set -e

crontab /etc/cron.d/mycron

touch /cron/last_code.txt

service cron start || cron

exec uvicorn api:app --host 0.0.0.0 --port 8080
