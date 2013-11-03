[supervisord]
logfile = %(here)s/logs/supervisor.log
loglevel = info
pidfile = %(here)s/run/supervisord.pid
directory = %(here)s/code

[unix_http_server]
file = %(here)s/run/supervisord.sock
chown = www-data:www-data
chmod = 0770

[supervisorctl]
serverurl = unix:///%(here)s/run/supervisord.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[group:web]
programs=p1

[program:p1]
command = %(here)s/env/bin/uwsgi --home %(here)s/env/ --socket %(here)s/run/per4.com.1.sock --chmod-socket --module uwsgi_app_live --pythonpath %(here)s/code
process_name = %(program_name)s
autostart = true
startretries=10
autorestart=true
startsecs = 5
user = www-data
redirect_stderr = true
stdout_logfile = %(here)s/logs/python.log
environment=PYTHONPATH=%(here)s/code

[program:p2]
command = %(here)s/env/bin/uwsgi --home %(here)s/env/ --socket %(here)s/run/per4.com.2.sock --chmod-socket --module uwsgi_app_live --pythonpath %(here)s/code
process_name = %(program_name)s
autostart = true
startretries=10
autorestart=true
startsecs = 5
user = www-data
redirect_stderr = true
stdout_logfile = %(here)s/logs/python.log
environment=PYTHONPATH=%(here)s/code
