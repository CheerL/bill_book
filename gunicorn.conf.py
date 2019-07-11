from settings import HOST, PORT

# bind = 'unix:/tmp/bill_book_backend.sock'
bind = '%s:%d' % (HOST, PORT)
workers = 2
worker_class = 'gevent'
timeout = 30
threads = 4