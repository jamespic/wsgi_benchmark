#!/bin/sh
exec uwsgi --http 0.0.0.0:8765 --master --module wsgi_benchmark.handlers --processes $(($(nproc) * 2))
