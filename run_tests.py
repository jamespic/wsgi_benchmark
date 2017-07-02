#!/usr/bin/env python
import contextlib
import subprocess
import os.path
import time

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


@contextlib.contextmanager
def server(command):
    server_process = subprocess.Popen(
        command, stderr=dev_null, stdout=dev_null)
    print "Running", server_name, "pid", server_process.pid
    try:
        yield
    finally:
        server_process.terminate()
        time.sleep(5)
        server_process.kill()
        subprocess.call('pgrep -f ping_pong_server | xargs -n 1 kill -SIGKILL',
                        shell=True)


if __name__ == '__main__':
    dev_null = open('/dev/null', 'w')
    with open('misc_results.txt', 'w') as misc_results:
        for server_name, command in SERVERS.items():
            with server(command):
                hash_result = subprocess.check_output(
                    'head -c 65536 /dev/zero | sha512sum', shell=True)
                success = hash_result == '73e4153936dab198397b74ee9efc26093dda721eaab2f8d92786891153b45b04265a161b169c988edb0db2c53124607b6eaaa816559c5ce54f3dbc9fa6a7a4b2'
                misc_results.write(
                    '{server_name}-chunked: {success}\n'.format(**locals()))

            with server(command):
                interrupted_result = subprocess.call(
                    ['curl', 'http://localhost:8765/interrupted'])
                success = interrupted_result != 0
                misc_results.write(
                    '{server_name}-interrupted: {success}\n'.format(**locals()))
            
            for scenario_name, scenario_class in GATLING_SCENARIOS.items():
                with server(command):
                    subprocess.call(
                        [
                            'mvn',
                            '-Dgatling.simulationClass=io.github.jamespic.wsgi_benchmark.%s' % scenario_class,
                            '-Dgatling.outputName=%s-%s' % (
                                scenario_name, server_name),
                            'integration-test'

                        ],
                        cwd=os.path.abspath('gatling')
                    )
