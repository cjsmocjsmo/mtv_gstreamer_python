gst-launch-1.0 filesrc location=/home/pipi/testvid.mp4 ! decodebin ! \
    queue ! xvimagesink fullscreen=true & \
    queue ! autoaudiosink
