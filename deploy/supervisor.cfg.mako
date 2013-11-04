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

[program:p1]
command = %(here)s/env/bin/uwsgi --home %(here)s/env/ --module webshop.wsgi:application --socket %(here)s/run/per4.com.1.sock
process_name = %(program_name)s
autostart = true
startretries=10
autorestart=true
startsecs = 5
user = www-data
redirect_stderr = true
stdout_logfile = %(here)s/logs/python.1.log
environment=PYTHONPATH=%(here)s/code/current;DJANGO_SETTINGS_MODULE=webshop.settings.${env}

[program:p2]
command = %(here)s/env/bin/uwsgi --home %(here)s/env/ --module webshop.wsgi:application --socket %(here)s/run/per4.com.2.sock
process_name = %(program_name)s
autostart = true
startretries=10
autorestart=true
startsecs = 5
user = www-data
redirect_stderr = true
stdout_logfile = %(here)s/logs/python.2.log
environment=PYTHONPATH=%(here)s/code/current;DJANGO_SETTINGS_MODULE=webshop.settings.${env}
