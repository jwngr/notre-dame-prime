import multiprocessing

# TODO: update name
name = 'primes'
bind = '127.0.0.1:8000'
errorlog = 'errors.log'
workers = multiprocessing.cpu_count() * 2 + 1
