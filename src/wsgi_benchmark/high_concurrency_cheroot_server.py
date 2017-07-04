from cheroot.wsgi import Server
from wsgi_benchmark.handlers import app
from multiprocessing import cpu_count

if __name__ == '__main__':
    httpd = Server(('0.0.0.0', 8765), app, numthreads=cpu_count() * 10)
    httpd.safe_start()
