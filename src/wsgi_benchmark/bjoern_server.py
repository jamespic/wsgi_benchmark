from bjoern import run
from wsgi_benchmark.handlers import app

if __name__ == '__main__':
    run(app, '0.0.0.0', 8765)
