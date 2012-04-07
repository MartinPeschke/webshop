#!/bin/bash

# Replace these three settings.
PROJDIR="/opt/sites/www.per-4.com/WebShop"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="$PROJDIR/mysite.sock"


export DJANGO_SETTINGS_MODULE=WebShop.settings

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

exec /usr/bin/env - \
  PYTHONPATH="../python2.5:.." \
  ./manage.py runfcgi socket=$SOCKET pidfile=$PIDFILE
