#!/bin/sh
exec gunicorn -w $(nproc) -k gevent -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
