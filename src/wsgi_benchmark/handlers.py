from __future__ import absolute_import
from contextlib import closing
import atexit
import hashlib
import os
import random
import socket
import subprocess
import sys
import tempfile
import zlib
from wsgiref.util import shift_path_info, FileWrapper
from wsgi_benchmark.native import triangular_nogil, native_wait


ping_pong_port = random.randint(32768, 65535)
ping_pong_process = subprocess.Popen(['python', '-m', 'wsgi_benchmark.ping_pong_server', str(ping_pong_port)])
atexit.register(ping_pong_process.kill)


fd, served_file = tempfile.mkstemp()
with os.fdopen(fd, 'w') as f:
    f.truncate(1024 ** 3)  # 1GB


@atexit.register
def cleanup():
    os.remove(served_file)


def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
    return ["Hello World"]


def numeric_nogil(environ, start_response):
    result = str(triangular_nogil(1.0))
    start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
    return [result]


def native_io(environ, start_response):
    native_wait(1.0)
    start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
    return ["Success"]


def socket_io(environ, start_response):
    with closing(socket.create_connection(('localhost', ping_pong_port))) as sock:
        sock.send('PING')
        response = sock.recv(4)
        start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
        return [response]


def interrupted(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
    yield "Hello"
    try:
        1/0
    except:
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain; charset=ascii')], sys.exc_info())
    yield "YOU SHOULD NOT BE HERE"


def sha512(environ, start_response):
    length = environ.get('CONTENT_LENGTH')
    digest = hashlib.sha512()
    body = environ['wsgi.input']
    if length:
        length = int(length)
        while length > 0:
            to_read = min(65536, length)
            length -= to_read
            digest.update(body.read(to_read))
    else:
        while True:
            data = body.read(65536)
            if data == '':
                break
            digest.update(data)
    start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
    return [digest.hexdigest()]


def gzip(environ, start_response):
    length = environ.get('CONTENT_LENGTH')
    compressor = zlib.compressobj(9, zlib.DEFLATED, 31)
    body = environ['wsgi.input']
    start_response('200 OK', [('Content-Type', 'application/octet-stream')])
    if length:
        length = int(length)
        while length > 0:
            to_read = min(65536, length)
            length -= to_read
            yield compressor.compress(body.read(to_read))
    else:
        while True:
            data = body.read(65536)
            if data == '':
                break
            yield compressor.compress(data)
    yield compressor.flush(zlib.Z_FINISH)


def serve_file(environ, start_response):
    f = open(served_file)
    wrapper = environ.get('wsgi.file_wrapper', FileWrapper)
    start_response('200 OK',
                   [('Content-Type', 'application/octet-stream')])
    return wrapper(f)


def http404(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain; charset=ascii')])
    return ["Not Found"]


_handlers = {
    'hello_world': hello_world,
    'numeric_nogil': numeric_nogil,
    'native_io': native_io,
    'socket_io': socket_io,
    'sha512': sha512,
    'sendfile': serve_file,
    'interrupted': interrupted,
    'gzip': gzip
}


def app(environ, start_response):
    path = shift_path_info(environ)
    return _handlers.get(path, http404)(environ, start_response)
