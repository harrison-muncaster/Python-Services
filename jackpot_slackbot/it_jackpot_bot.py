import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import bf_logging
from bf_rig import settings
import bf_tornado.handlers.rig

from handlers.action import ActionHandler
from handlers.base import HealthHandler
from handlers.slash import SlashHandler


class Application(tornado.web.Application):
    def __init__(self):
        app_settings = {
            'default_handler_class': bf_tornado.handlers.rig.NotFoundHandler,
            'debug': settings.get('debug'),
        }
        app_handlers = [
            (r'^/action$', ActionHandler),
            (r'^/slash$', SlashHandler),
            (r'^/health$', HealthHandler),
        ]
        super(Application, self).__init__(app_handlers, **app_settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()

    logger = bf_logging.Log()

    port = settings.get('port')
    logger.info('service %s listening on port %d', settings.get('service'), port)

    http_server = tornado.httpserver.HTTPServer(
        request_callback=Application(), xheaders=True)
    http_server.listen(port)

    tornado.ioloop.IOLoop.instance().start()
