#!/bin/bash
set -e  # Exit on error

DPI=96
RES_AND_DEPTH=${WIDTH}x${HEIGHT}x24

# Function to check if Xvfb is already running and display is usable
check_xvfb_running() {
    if xdpyinfo >/dev/null 2>&1; then
        return 0  # Display is responsive
    fi
    # Clean up stale lock/socket files so Xvfb can start cleanly
    rm -f /tmp/.X${DISPLAY_NUM}-lock /tmp/.X11-unix/X${DISPLAY_NUM}
    return 1
}

# Function to check if Xvfb is ready
wait_for_xvfb() {
    local timeout=10
    local start_time=$(date +%s)
    while ! xdpyinfo >/dev/null 2>&1; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Xvfb failed to start within $timeout seconds" >&2
            return 1
        fi
        sleep 0.1
    done
    return 0
}

# Check if Xvfb is already running
if check_xvfb_running; then
    echo "Xvfb is already running on display ${DISPLAY}"
    exit 0
fi

# Start Xvfb
Xvfb $DISPLAY -ac -screen 0 $RES_AND_DEPTH -retro -dpi $DPI -nolisten tcp -nolisten unix &
XVFB_PID=$!

# Wait for Xvfb to start
if wait_for_xvfb; then
    echo "Xvfb started successfully on display ${DISPLAY}"
    echo "Xvfb PID: $XVFB_PID"
else
    echo "Xvfb failed to start"
    kill $XVFB_PID
    exit 1
fi
