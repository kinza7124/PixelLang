#!/usr/bin/env bash
# Headless launcher for PixelLang GUI using Xvfb
# Usage: bash run_headless.sh

LOG=run_headless.log
PIDFILE=run_headless.pid

# Start under Xvfb and capture PID
xvfb-run -a python main.py &> "$LOG" &
PID=$!
echo $PID > "$PIDFILE"
echo "Started PixelLang GUI (headless) with PID $PID; logs -> $LOG"
