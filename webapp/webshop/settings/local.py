# Django settings for webshop project.
from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

GOOGLE_TRACKING = ''
SECRET_KEY= '123'

DATABASES = {
    'default': {
         'ENGINE':'django.db.backends.mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        ,'NAME':'devel'           # Or path to database file if using sqlite3.
        ,'USER':'root'             # Not used with sqlite3.
        ,'PASSWORD':'199xuxr0c'         # Not used with sqlite3.
        ,'HOST':'localhost'             # Set to empty string for localhost. Not used with sqlite3.
        ,'PORT':'3306'             # Set to empty string for default. Not used with sqlite3.
    }, 'articledb': {
         'ENGINE':'django.db.backends.mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        ,'NAME':'devel'           # Or path to database file if using sqlite3.
        ,'USER':'root'             # Not used with sqlite3.
        ,'PASSWORD':'199xuxr0c'         # Not used with sqlite3.
        ,'HOST':'localhost'             # Set to empty string for localhost. Not used with sqlite3.
        ,'PORT':'3306'             # Set to empty string for default. Not used with sqlite3.
    }
}