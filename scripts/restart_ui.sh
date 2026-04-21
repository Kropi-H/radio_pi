#!/bin/bash
pkill -f "chromium.*127.0.0.1:5000" || pkill chromium || true
sleep 1
nohup chromium --kiosk --app=http://127.0.0.1:5000 >/dev/null 2>&1 &
