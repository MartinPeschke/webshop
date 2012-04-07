= Setup Envirnoment =
== Create Database & User ==

{{{
CREATE USER devel;
CREATE DATABASE webshop;
SET PASSWORD FOR 'devel'@'localhost' = PASSWORD('devel');
GRANT ALL ON webshop.* TO 'devel'@'localhost';
}}}
== Sync DB ==
{{{
python manage.py syncdb
}}}
== Start Server ==
{{{
. ./setup-env.sh
python manage.py runserver 8080
}}}


test