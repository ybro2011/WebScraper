import multiprocessing
import os

# Gunicorn config variables
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5

# Logging
capture_output = True
errorlog = "/home/LogFiles/gunicorn_error.log"
accesslog = "/home/LogFiles/gunicorn_access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Reload
reload = False
preload_app = True 