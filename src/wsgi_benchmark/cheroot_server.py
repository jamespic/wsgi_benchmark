from cheroot.wsgi import Server
from wsgi_benchmark.handlers import app

if __name__ == '__main__':
    httpd = Server(('0.0.0.0', 8765), app)
    httpd.safe_start()
