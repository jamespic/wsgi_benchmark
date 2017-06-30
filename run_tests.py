#!/usr/bin/env python
import subprocess
import os.path
import time
import signal

SERVERS = {
    'bjoern': ['python', '-m', 'wsgi_benchmark.bjoern_server'],
    'cheroot': ['python', '-m', 'wsgi_benchmark.cheroot_server'],
    'cheroot_high_concurrency': ['python', '-m', 'wsgi_benchmark.high_concurrency_cheroot_server'],
    'eventlet': ['python', '-m', 'wsgi_benchmark.eventlet_server'],
    'gunicorn': ['./gunicorn_server.sh'],
    'gunicorn_gevent': ['./gevent_gunicorn_server.sh'],
    'gunicorn_gthread': ['./gthread_gunicorn_server.sh'],
    'gunicorn_eventlet': ['./eventlet_gunicorn_server.sh'],
    'gunicorn_high_concurrency': ['./high_concurrency_gunicorn_server.sh'],
    'gevent': ['python', '-m', 'wsgi_benchmark.gevent_server'],
    'meinheld': ['python', '-m', 'wsgi_benchmark.meinheld_server'],
    'waitress': ['python', '-m', 'wsgi_benchmark.waitress_server'],
    'waitress_high_concurrency': ['python', '-m', 'wsgi_benchmark.high_concurrency_waitress_server'],
    'werkzeug': ['python', '-m', 'wsgi_benchmark.werkzeug_server'],
    'werkzeug_threading': ['python', '-m', 'wsgi_benchmark.threading_werkzeug_server'],
    'werkzeug_forking': ['python', '-m', 'wsgi_benchmark.forking_werkzeug_server'],
    'wsgiref': ['python', '-m', 'wsgi_benchmark.wsgiref_server'],
    'wsgiref_threading': ['python', '-m', 'wsgi_benchmark.threading_wsgiref_server'],
    'wsgiref_forking': ['python', '-m', 'wsgi_benchmark.forking_wsgiref_server']
}

GATLING_SCENARIOS = {
    'hello_world': 'HelloWorldSimulation',
    'numeric_nogil': 'NumericNoGilSimulation',
    'native_io': 'NativeIOSimulation',
    'socket_io': 'SocketIOSimulation',
    'sendfile': 'SendfileSimulation',
    'sha512': 'SHA512Simulation',
    'forward_request': 'ForwardSimulation',
    'gzip': 'GzipSimulation'
}

if __name__ == '__main__':
    dev_null = open('/dev/null', 'w')
    for server_name, command in SERVERS.items():
        for scenario_name, scenario_class in GATLING_SCENARIOS.items():
            server_process = subprocess.Popen(command, stderr=dev_null, stdout=dev_null)
            print "Running", server_name, "pid", server_process.pid
            try:
                test_status = subprocess.call(
                    [
                        'mvn',
                        '-Dgatling.simulationClass=io.github.jamespic.wsgi_benchmark.%s' % scenario_class,
                        '-Dgatling.outputName=%s-%s' % (scenario_name, server_name),
                        'integration-test'

                    ],
                    cwd=os.path.abspath('gatling')
                )
            finally:
                server_process.terminate()
                time.sleep(5)
                server_process.kill()
