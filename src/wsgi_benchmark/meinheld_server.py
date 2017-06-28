if __name__ == '__main__':
    from meinheld import server
    from meinheld.patch import patch_socket
    patch_socket()
    from wsgi_benchmark.handlers import app
    server.listen(('0.0.0.0', 8765))
    server.run(app)
