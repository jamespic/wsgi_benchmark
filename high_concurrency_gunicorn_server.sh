#!/bin/sh
exec gunicorn -w $(($(nproc) * 10)) -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
