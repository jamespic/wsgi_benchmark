if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    from gevent.pywsgi import WSGIServer
    from wsgi_benchmark.handlers import app

    server = WSGIServer(('', 8765), app)
    server.serve_forever()
