from waitress import serve
from wsgi_benchmark.handlers import app

if __name__ == '__main__':
    serve(app, listen='*:8765', threads=50)
