# Django settings for WebShop project.
import random
import os

_ = lambda s: s

here = os.path.abspath(os.path.join(__file__, ".."))
VERSION_FILE = os.path.join(here, "VERSION_TOKEN")

if os.path.exists(VERSION_FILE):
    STATIC_VERSION_TOKEN = open(VERSION_FILE).read().strip()
else:
    STATIC_VERSION_TOKEN = random.random()


DEBUG = True
TEMPLATE_DEBUG = True

USE_I18N = True

ADMINS = (
    ('admin', 'martin.peschke@gmx.net'),
)

SHOP_NAME = 'per-4.com'
DEFAULT_SHOP ='piercing'
# Make this unique, and don't share it with anybody.
SECRET_KEY = '&rl9146h%z6o+ph(8xap24@@ohy@o#5@7st@d69*v**ol(44v@'
BOP_PUBLIC = 'b259a54d7febad1f979ef801d2ca3b2198f090cb'

# ---------------------- Basic Django - Customized for Per4 --------------------------
# Email
DEFAULT_FROM_EMAIL = 'webshop@per-4.com'
EMAIL_HOST = 'post.strato.de'
EMAIL_HOST_USER = 'webshop@per-4.net'
EMAIL_HOST_PASSWORD = 'VANV6f}Jq0!{'
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = '[PER4]'
SERVER_EMAIL = 'martin@per-4.net'
ORDER_MAIL = 'martin@per-4.net'
ERROR_MAIL = 'martin@per-4.net'

TAX_RATE = 19.0
ARTICLE_LINE_PANE_SIZE = 8
CACHE_TIMEOUT = 604800
TITLE_CHOICES = ( 
    ('MR', _('MR.')),
    ('MRS', _('MRS.')),
    ('MS', _('MS.')),
)

GOOGLE_TRACKING = '''<script type="text/javascript">
                var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
                document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
            </script>
            <script type="text/javascript">
                var pageTracker = _gat._getTracker("UA-1907986-1");
                pageTracker._initData();
                pageTracker._trackPageview();
            </script>'''



FB_APP_ID="369049056473174"
FB_APP_SECRET="8d775ba60036d30ee74586ed0771610e"

# ---------------------- Basic Django --------------------------

# Logger
LOG_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), 'shop.log'))

# Misc
CACHE_BACKEND = 'locmem:///'
INTERNAL_IPS = '127.0.0.1'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'WebShop', 'templates'),)
LOCALE_PATHS = (
    'd:/home/Martin/Documents/python/ws/webshop/WebShop/locale',
    os.path.join(os.path.dirname(__file__), 'WebShop', 'locale'),)
DATABASES = {
    'default': {
         'ENGINE':'django.db.backends.mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        ,'NAME':'per4_database'           # Or path to database file if using sqlite3.
        ,'USER':'root'             # Not used with sqlite3.
        ,'PASSWORD':'199xuxr0c'         # Not used with sqlite3.
        ,'HOST':'localhost'             # Set to empty string for localhost. Not used with sqlite3.
        ,'PORT':'3306'             # Set to empty string for default. Not used with sqlite3.
    },	'articledb': {
         'ENGINE':'django.db.backends.mysql'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        ,'NAME':'per4_database'           # Or path to database file if using sqlite3.
        ,'USER':'root'             # Not used with sqlite3.
        ,'PASSWORD':'199xuxr0c'         # Not used with sqlite3.
        ,'HOST':'localhost'             # Set to empty string for localhost. Not used with sqlite3.
        ,'PORT':'3306'             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Berlin'

SITE_ID = 1


# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT=os.path.normpath(os.path.join(os.path.dirname(__file__), 'WebShop', 'static'))
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'WebShop', 'media'))
DATA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'WebShop', 'data'))

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
# from django.utils.translation import gettext_lazy as _
LANGUAGE_CODE = 'en'
MANAGERS = ADMINS

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'WebShop.apps.contrib.middleware.random_promo_processor',
    'WebShop.apps.contrib.middleware.cart_shops_processor',
    'django.contrib.auth.context_processors.auth',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'WebShop.urls'

MIDDLEWARE_CLASSES = (
   'django.middleware.common.CommonMiddleware',
   'django.contrib.sessions.middleware.SessionMiddleware',
   'django.middleware.locale.LocaleMiddleware',
   'django.contrib.auth.middleware.AuthenticationMiddleware',
   'django.contrib.messages.middleware.MessageMiddleware'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'WebShop.apps.contrib.countries',
    'WebShop.apps.order',
    'WebShop.apps.explore',
    'WebShop.apps.user',
    'WebShop.apps.search',
    'WebShop.apps.service',
    'WebShop.apps.cms',
    'bootstrap',
)


AUTHENTICATION_BACKENDS = (
    'WebShop.apps.user.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = 'user.Profile'
ACTIVATE_ROOT = '/user/activate/'

