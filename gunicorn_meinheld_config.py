import multiprocessing
workers = multiprocessing.cpu_count()
worker_class = "egg:meinheld#gunicorn_worker"
bind = ["0.0.0.0:8765"]

def post_fork(server, worker):
    from meinheld.patch import patch_socket
    patch_socket()
