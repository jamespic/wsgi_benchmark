#!/bin/sh
exec gunicorn -w $(nproc) --worker-class="egg:meinheld#gunicorn_worker" -b 0.0.0.0:8765 wsgi_benchmark.handlers:app
