bind = "0.0.0.0:9001"
loglevel = "INFO"
workers = "3"
reload = True

timeout = 90

forwarded_allow_ips = '*'

import datetime
current_date = str(datetime.date.today())

errorlog = "/log/%s-gunicorn_error.log" % current_date
accesslog = "/log/%s-gunicorn_access.log" % current_date

chdir='/data'
