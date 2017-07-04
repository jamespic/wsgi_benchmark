from waitress import serve
from wsgi_benchmark.handlers import app
from multiprocessing import cpu_count

if __name__ == '__main__':
    serve(app, listen='*:8765', threads=cpu_count() * 10)
