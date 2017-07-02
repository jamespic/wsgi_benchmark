#!/usr/bin/env python
from setuptools import setup, find_packages, Extension
setup(
    name="wsgi_benchmark",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=[
        'cython'
    ],
    install_requires=[
        'cheroot',
        'waitress',
        'bjoern',
        'werkzeug',
        'gunicorn',
        'gevent',
        'eventlet',
        'meinheld',
        'futures'
    ],
    ext_modules=[
        Extension('wsgi_benchmark.native',
                  ["src/wsgi_benchmark/native.pyx"])
    ]

)
