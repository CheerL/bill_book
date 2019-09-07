from settings import HOST, PORT

#bind = 'unix:/var/run/billbook/billbook.sock'
bind = '%s:%d' % (HOST, PORT)
workers = 2
worker_class = 'gevent'
timeout = 30
threads = 4
