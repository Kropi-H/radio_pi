#!/bin/bash
pkill -f "chromium.*127.0.0.1:5000" || pkill chromium || true
