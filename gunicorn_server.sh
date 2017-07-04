#!/bin/sh
exec gunicorn -w $(($(nproc) * 2)) -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
