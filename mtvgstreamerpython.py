import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk

import uvicorn
from fastapi import FastAPI

app = FastAPI()
pipeline = None
drawing_area = None  # Holds the video display area

@app.on_event("startup")
async def startup_event():
    Gst.init(None)

@app.post("/start/{path}")
async def start_video(path: str):
    global pipeline, drawing_area

    if pipeline:
        pipeline.set_state(Gst.State.NULL)

    # Create GTK window
    window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit) # Stop on window close
    window.set_default_size(800, 600)  # Adjust default size if needed

    # Create drawing area for video
    # drawing_area = Gtk.DrawingArea()
    # window.add(drawing_area)
    path = "/home/pipi/" + path
    print(f"Playing video: {path}")

    # Create GStreamer pipeline
    pipeline = Gst.parse_launch(f"playbin uri={path}")

    # Override video sink to use the GTK window
    # bus = pipeline.get_bus()
    # bus.add_signal_watch() 
    # bus.connect("message::element", on_message)

    pipeline.set_state(Gst.State.PLAYING)
    window.show_all()
    # window.fullscreen()  
    Gtk.main()
    return {"message": "Video started"}

def on_message(bus, message):
    t = message.type
    if t == Gst.MessageType.EOS:
        pipeline.set_state(Gst.State.NULL)
    elif t == Gst.MessageType.ERROR:
        pipeline.set_state(Gst.State.NULL)
        err, debug = message.parse_error()
        print(f"GStreamer Error: {err}, {debug}")
    elif t == Gst.MessageType.STATE_CHANGED:
        old_state, new_state, pending_state = message.parse_state_changed()
        if new_state == Gst.State.PLAYING:
            # Embed GStreamer video into the GTK window
            xid = drawing_area.get_window().get_xid()
            videosink = message.src
            videosink.set_window_handle(xid)

@app.post("/stop")
async def stop_video():
    global pipeline
    if pipeline:
        pipeline.set_state(Gst.State.NULL)
        pipeline = None
    return {"message": "Video stopped"}

@app.post("/pause")
async def pause_video():
    global pipeline
    if pipeline:
        pipeline.set_state(Gst.State.PAUSED)
    return {"message": "Video paused"}

@app.post("/play")
async def play_video():
    global pipeline
    if pipeline:
        pipeline.set_state(Gst.State.PLAYING)
    return {"message": "Video resumed"}

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.91", port=8000)
