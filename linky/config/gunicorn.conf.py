import multiprocessing

appname = "linky"

procname = appname

bind = "unix:/tmp/%s" % appname
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1000
preload_app = True

accesslog = "/home/webapp/apps/linky/logs/access.log"
errorlog = "/home/webapp/apps/linky/logs/error.log"
loglevel = "info"
