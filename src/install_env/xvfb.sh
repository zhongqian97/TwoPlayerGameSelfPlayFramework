Xvfb :10 -screen 0 1024x768x16 &
export DISPLAY=:10
disown %1

# Xvfb :0 -screen 0 1920x1080x24 -listen tcp -ac +extension GLX +extension RENDER
