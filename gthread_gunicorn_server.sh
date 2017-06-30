#!/bin/sh
exec gunicorn -w 4 -k gthread -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
