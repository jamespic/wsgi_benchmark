#!/usr/bin/env python
import contextlib
import docker
import subprocess
import os.path
import sys
import time
import urllib2

SERVERS = {
    'bjoern': ['python', '-m', 'wsgi_benchmark.bjoern_server'],
    'cheroot': ['python', '-m', 'wsgi_benchmark.cheroot_server'],
    'cheroot_high_concurrency': ['python', '-m', 'wsgi_benchmark.high_concurrency_cheroot_server'],
    'eventlet': ['python', '-m', 'wsgi_benchmark.eventlet_server'],
    'gunicorn': ['./gunicorn_server.sh'],
    'gunicorn_gevent': ['./gevent_gunicorn_server.sh'],
    'gunicorn_gthread': ['./gthread_gunicorn_server.sh'],
    'gunicorn_meinheld': ['./meinheld_gunicorn_server.sh'],
    'gunicorn_high_concurrency': ['./high_concurrency_gunicorn_server.sh'],
    'gevent': ['python', '-m', 'wsgi_benchmark.gevent_server'],
    'meinheld': ['python', '-m', 'wsgi_benchmark.meinheld_server'],
    'uwsgi': ['./uwsgi_server.sh'],
    'uwsgi_gevent': ['./gevent_uwsgi_server.sh'],
    'uwsgi_high_concurrency': ['./high_concurrency_uwsgi_server.sh'],
    'uwsgi_threaded': ['./threaded_uwsgi_server.sh'],
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
    'dynamic_file': 'DynamicFileSimulation',
    'sha512': 'SHA512Simulation',
    'forward_request': 'ForwardSimulation',
    'gzip': 'GzipSimulation',
    'numeric_gil': 'NumericGilSimulation'
}


def build_image():
    docker.from_env().images.build(path='.', tag='wsgi_benchmark')


@contextlib.contextmanager
def server(command, server_name):
    container = docker.from_env().containers.run(
        'wsgi_benchmark', command,
        name='wsgi_benchmark-{}'.format(server_name),
        detach=True, ports={'8765/tcp': 8765})
    print "{server_name} running as container {container.id}".format(**locals())
    try:
        for i in xrange(30):
            try:
                assert urllib2.urlopen('http://localhost:8765/hello_world').read() == 'Hello World'
            except:
                time.sleep(1)
            else:
                break
        else:
            raise RuntimeError("Could not start server process: {}" .format(server_name))
        yield container
    finally:
        container.remove(force=True)


if __name__ == '__main__':
    build_image()
    for server_name, server_command in sorted(SERVERS.items()):
        print "Testing {server_name} starts".format(**locals())
        with server(server_command, server_name):
            print "Success"
    with open('results/misc_results.txt', 'w') as misc_results:
        for server_name, command in sorted(SERVERS.items()):
            with server(command, server_name):
                try:
                    hash_result = subprocess.check_output(
                        'head -c 65536 /dev/zero | curl -T - -y 5 http://localhost:8765/sha512', shell=True)
                    success = hash_result == '73e4153936dab198397b74ee9efc26093dda721eaab2f8d92786891153b45b04265a161b169c988edb0db2c53124607b6eaaa816559c5ce54f3dbc9fa6a7a4b2'
                except:
                    success = False
                misc_results.write(
                    '{server_name}-chunked: {success}\n'.format(**locals()))

            with server(command, server_name):
                interrupted_result = subprocess.call(
                    ['curl', 'http://localhost:8765/interrupted'])
                success = interrupted_result != 0
                misc_results.write(
                    '{server_name}-interrupted: {success}\n'.format(**locals()))

            with server(command, server_name):
                subprocess.call(['slowhttptest', '-g', '-X',
                                 '-v', '1',
                                 '-i', '3',
                                 '-l', '30',
                                 '-c', '300',
                                 '-o', '{server_name}-slow_read'.format(**locals()),
                                 '-u', 'http://localhost:8765/dynamic_file'], cwd='results')

            with server(command, server_name):
                subprocess.call(['slowhttptest', '-g', '-H',
                                 '-v', '1',
                                 '-i', '3',
                                 '-l', '30',
                                 '-c', '300',
                                 '-o', '{server_name}-slow_headers'.format(**locals()),
                                 '-u', 'http://localhost:8765/hello_world'], cwd='results')

            with server(command, server_name):
                subprocess.call(['slowhttptest', '-g', '-B',
                                 '-v', '1',
                                 '-i', '3',
                                 '-l', '30',
                                 '-c', '300',
                                 '-o', '{server_name}-slow_body'.format(**locals()),
                                 '-u', 'http://localhost:8765/sha512'], cwd='results')

            for scenario_name, scenario_class in sorted(GATLING_SCENARIOS.items()):
                with server(command, server_name) as server_container:
                    container = docker.from_env().containers.run(
                        'wsgi_benchmark',
                        [
                            'mvn',
                            '-Dgatling.simulationClass=io.github.jamespic.wsgi_benchmark.%s' % scenario_class,
                            '-Dgatling.outputName=%s-%s' % (
                                scenario_name, server_name),
                            '-Dgatling.resultsFolder=/results',
                            'integration-test'

                        ],
                        name='wsgi_benchmark_gatling_{scenario_name}_{server_name}'.format(**locals()),
                        links={server_container.name: 'wsgi_benchmark_server'},
                        volumes={os.path.abspath('results'): {'bind': '/results', 'mode': 'rw'}},
                        environment={'TARGET_HOSTNAME': 'wsgi_benchmark_server'},
                        working_dir='/wsgi_benchmark/gatling',
                        detach=True
                    )
                    try:
                        for line in container.logs(stdout=True, stderr=True, stream=True):
                            sys.stdout.write(line)
                    finally:
                        container.remove(force=True)
