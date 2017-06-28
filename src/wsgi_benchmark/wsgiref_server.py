from __future__ import absolute_import
from wsgiref.simple_server import make_server
from wsgi_benchmark.handlers import app

if __name__ == '__main__':
    server = make_server('', 8765, app)
    server.serve_forever()
