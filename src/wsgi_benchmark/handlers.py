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
from werkzeug.wsgi import get_input_stream
from wsgiref.util import FileWrapper, shift_path_info
from wsgi_benchmark.native import triangular_nogil, native_wait


TEXT_HEADER = [('Content-Type', 'text/plain; charset=ascii')]
BINARY_HEADER = [('Content-Type', 'application/octet-stream')]


ping_pong_port = random.randint(32768, 65535)
ping_pong_process = subprocess.Popen(['python', '-m', 'wsgi_benchmark.ping_pong_server', str(ping_pong_port)])
atexit.register(ping_pong_process.kill)


def ping():
    with closing(socket.create_connection(('localhost', ping_pong_port))) as sock:
        sock.send('PING')
        return sock.recv(4)


fd, served_file = tempfile.mkstemp()
with os.fdopen(fd, 'w') as f:
    f.truncate(1024 ** 2)  # 1MB


@atexit.register
def cleanup():
    os.remove(served_file)


def hello_world(environ, start_response):
    start_response('200 OK', TEXT_HEADER)
    return ["Hello World"]


def numeric_nogil(environ, start_response):
    result = str(triangular_nogil(1.0))
    start_response('200 OK', TEXT_HEADER)
    return [result]


def numeric_gil(environ, start_response):
    result = str(sum(xrange(200000000)))
    start_response('200 OK', TEXT_HEADER)
    return [result]


def native_io(environ, start_response):
    native_wait(1.0)
    start_response('200 OK', TEXT_HEADER)
    return ["Success"]


def socket_io(environ, start_response):
    response = ping()
    start_response('200 OK', TEXT_HEADER)
    return [response]


def interrupted(environ, start_response):
    start_response('200 OK', TEXT_HEADER)
    yield "Hello"
    try:
        1/0
    except:
        start_response('500 Internal Server Error', TEXT_HEADER, sys.exc_info())
    yield "YOU SHOULD NOT BE HERE"


def sha512(environ, start_response):
    digest = hashlib.sha512()
    body = get_input_stream(environ, safe_fallback=False)
    while True:
        data = body.read(65536)
        if data == '':
            break
        digest.update(data)
    start_response('200 OK', TEXT_HEADER)
    return [digest.hexdigest()]


def gzip(environ, start_response):
    compressor = zlib.compressobj(9, zlib.DEFLATED, 31)
    body = get_input_stream(environ, safe_fallback=False)
    start_response('200 OK', BINARY_HEADER)
    while True:
        data = body.read(65536)
        if data == '':
            break
        yield compressor.compress(data)
    yield compressor.flush(zlib.Z_FINISH)


def forward_request(environ, start_response):
    body = get_input_stream(environ, safe_fallback=False)
    while True:
        data = body.read(65536)
        if data == '':
            break
        ping()
    start_response('200 OK', TEXT_HEADER)
    return ['Success']


def serve_file(environ, start_response):
    f = open(served_file)
    wrapper = environ.get('wsgi.file_wrapper', FileWrapper)
    start_response('200 OK', BINARY_HEADER)
    return wrapper(f)


def push_write(environ, start_response):
    writer = start_response('200 OK', BINARY_HEADER)
    chunk = '\0' * 1024
    for _ in xrange(1024):
        writer(chunk)
    return []


def dynamic_file(environ, start_response):
    start_response('200 OK', BINARY_HEADER)
    chunk = '\0' * 1024
    for _ in xrange(1024):
        yield chunk


def http404(environ, start_response):
    start_response('404 Not Found', TEXT_HEADER)
    return ["Not Found"]


_handlers = {
    'hello_world': hello_world,
    'numeric_nogil': numeric_nogil,
    'numeric_gil': numeric_gil,
    'native_io': native_io,
    'socket_io': socket_io,
    'sha512': sha512,
    'forward_request': forward_request,
    'sendfile': serve_file,
    'dynamic_file': dynamic_file,
    'push_write': push_write,
    'interrupted': interrupted,
    'gzip': gzip
}


def app(environ, start_response):
    path = shift_path_info(environ)
    return _handlers.get(path, http404)(environ, start_response)

application = app
