import tornado.ioloop
import tornado.web
import gi

gi.require_version('Gst')
from gi.repository import Gst

class VideoPlayerController(tornado.web.RequestHandler):
    def initialize(self):
        self.pipeline = Gst.Pipeline()
        # Replace with your video file path
        self.video_source = Gst.ElementFactory.make("filesrc", None)
        self.video_source.set_property("location", "/path/to/your/video.mp4")
        # Add other elements as needed (e.g., decoder, sink)
        
    def post(self, action):
        if action == "start":
            self.pipeline.add(self.video_source)
            self.pipeline.set_state(Gst.State.PLAYING)
            self.write("Video started")
        elif action == "stop":
            self.pipeline.set_state(Gst.State.NULL)
            self.write("Video stopped")
        elif action == "play":
            self.pipeline.set_state(Gst.State.PLAYING)
            self.write("Video resumed")
        elif action == "pause":
            self.pipeline.set_state(Gst.State.PAUSED)
            self.write("Video paused")
        else:
            self.write("Invalid action")

application = tornado.web.Application([
    (r"/video/(start|stop|play|pause)", VideoPlayerController),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
