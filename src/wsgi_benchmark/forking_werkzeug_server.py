from werkzeug.serving import make_server
from wsgi_benchmark.handlers import app
from multiprocessing import cpu_count

if __name__ == '__main__':
    server = make_server('', 8765, app, processes=cpu_count() * 10)
    server.serve_forever()
