if __name__ == '__main__':
    from eventlet import monkey_patch, wsgi
    import eventlet
    eventlet.sleep()
    monkey_patch()
    from wsgi_benchmark.handlers import app

    wsgi.server(eventlet.listen(('0.0.0.0', 8765)), app)
