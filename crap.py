import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, Gtk, Gdk, GObject

def on_pad_added(dbin, pad):
    # Link the newly generated pad from the decoder to the video sink
    pad.link(videosink.get_static_pad("sink"))

def on_sync_message(bus, message):
    if message.get_structure().get_name() == "prepare-window-handle":
        imagesink = message.src
        imagesink.set_property("force-aspect-ratio", True) 
        video_area.connect("draw", lambda wid, cr: imagesink.set_window_handle(wid.get_window().xid))

def on_eos(bus, msg):
    print("End-Of-Stream reached")
    pipeline.set_state(Gst.State.NULL)

def on_error(bus, msg):
    print("Error: ", msg.parse_error())
    pipeline.set_state(Gst.State.NULL)

# Initialize GStreamer and GTK+
Gst.init(None)
Gtk.init()

# Create the pipeline
pipeline = Gst.Pipeline.new("player")

# Create elements
filesrc = Gst.ElementFactory.make("filesrc", "source")
filesrc.set_property("location", "/home/charliepi/testvid.mp4")
decodebin = Gst.ElementFactory.make("decodebin", "decoder")
videosink = Gst.ElementFactory.make("autovideosink", "sink")

# Add elements to the pipeline
pipeline.add(filesrc)
pipeline.add(decodebin)
pipeline.add(videosink)

# Link the elements
filesrc.link(decodebin)

decodebin.connect("pad-added", on_pad_added)

# Create the window and video area
window = Gtk.Window()
video_area = Gtk.DrawingArea()
window.set_default_size(800, 600)
window.set_title("Video Player")
window.connect("destroy", Gtk.main_quit)


video_area.set_size_request(800, 600)
video_area.set_property("hexpand", True)
video_area.set_property("vexpand", True)
video_area.set_property('can-focus', False)  # Don't take focus from other elements
# video_area.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("black"))  # Set black background
window.add(video_area)

# Connect GStreamer bus to handle video overlay
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message::eos", on_eos)
bus.connect("message::error", on_error)
bus.enable_sync_message_emission()
bus.connect("sync-message::element", on_sync_message)

# Start playing
window.show_all()
pipeline.set_state(Gst.State.PLAYING)

Gtk.main()
