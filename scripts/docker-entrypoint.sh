#!/bin/bash
set -e

# Start Xvfb
Xvfb $DISPLAY -screen 0 $RESOLUTION -ac +extension GLX +render -noreset &

# Start window manager
fluxbox &

# Start VNC server
x11vnc -display $DISPLAY -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &

# Start noVNC
websockify --web /usr/share/novnc/ 6080 localhost:5900 &

echo "==================================================="
echo "VNC server running on port 5900"
echo "noVNC web interface available on port 6080"
echo "http://localhost:6080/vnc.html"
echo "==================================================="

exec "$@"
