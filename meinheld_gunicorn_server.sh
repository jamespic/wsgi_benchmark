#!/bin/sh
exec gunicorn -c gunicorn_meinheld_config.py wsgi_benchmark.handlers:app
