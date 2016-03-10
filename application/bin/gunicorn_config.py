import datetime

bind = "0.0.0.0:9001"
loglevel = "INFO"
workers = "3"
reload = True


current_date = str(datetime.datetime.today())

errorlog = "/log/%s-gunicorn_error.log" % current_date
accesslog = "/log/%s-gunicorn_access.log" % current_date
