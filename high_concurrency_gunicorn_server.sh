#!/bin/sh
exec gunicorn -w 50 -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
