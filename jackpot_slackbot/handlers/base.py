import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    """
    All requests inherit from this. It is company policy to remove
    server version identification, which Tornado adds by default.
    """
    def set_default_headers(self):
        """
        Don't identify Tornado/Tornado's version information.
        """
        self.clear_header('Server')

    def write_error(self, headers, **kwargs):
        """
        Override the default error message handler and send a generic emoji instead,
        in the spirit of not leaking information.
        """
        self.write('👎')


class HealthHandler(BaseHandler):
    """
    Health check handlers
    """
    def get(self):
        """
        Simply ensures the rig service is responding at all.
        """
        self.finish('OK')


class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Ensure errors are also sent through the BaseHandler.
    """
    pass
