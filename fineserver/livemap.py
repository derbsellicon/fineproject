import os
import json
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options

#logging.basicConfig(filename='example.log',level=logging.DEBUG)

log = logging.getLogger(__name__)
WEBSOCKS = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("static/map.html")

class RandomLatLngSender(tornado.web.RequestHandler):
    """When an HTTP request is sent to /ping,
    this class sends a random lat/lng coord out
    over all websocket connections
    """

    def get(self):
        global WEBSOCKS
        log.debug("pinging: %r" % WEBSOCKS)

        import random
        latlng = {
            'lat': random.randint(-90, 90),
            'lng': random.randint(-45, 45),
            #'lat': 48.83451,
            #'lng':  2.30951, 
            'title': "Marker!",
            }

        data = json.dumps(latlng)
        for sock in WEBSOCKS:
            sock.write_message(data)


class WebSocketBroadcaster(tornado.websocket.WebSocketHandler):
    """Keeps track of all websocket connections in
    the global WEBSOCKS variable.
    
    """
    def open(self):
        log.info("Opened socket %r" % self)
        global WEBSOCKS
        WEBSOCKS.append(self)

    def on_message(self, message):
        log.info(u"Got message from websocket: %s" % message)

    def on_close(self):
        log.info("Closed socket %r" % self)
        global WEBSOCKS
        WEBSOCKS.remove(self)

    def check_origin(self, origin):
        return True


settings = {
    "debug"      : True,
    'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
}
print settings

application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/ping", RandomLatLngSender),
        (r"/sock", WebSocketBroadcaster),
        ],
    **settings)


if __name__ == "__main__":
    define("port", default=8888, help="Run server on a specific port", type=int)
    tornado.options.parse_command_line()

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
