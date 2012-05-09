# Django settings for pantoto_lite project.
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from django.contrib.messages import constants as message_constants
import os

MESSAGE_TAGS = {
        message_constants.DEBUG: 'debug',
        message_constants.INFO: 'info',
        message_constants.SUCCESS: 'alert_success',
        message_constants.WARNING: 'warning',
        message_constants.ERROR: 'alert_error'
}

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'cms')

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.csrf',
    'django.core.context_processors.request',
    'cms.context_processors.common_context',
)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {

    'default': {
        'ENGINE': '',
        'NAME': 'pantotodb',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '27017',
        'SUPPORTS_TRANSACTIONS': False,
    },
 
}

#Mongo database settings
MONGO_DBNAME = 'pantotodb'
MONGO_HOST = 'localhost'
MONGO_PORT = '27017' 
MONGO_USERNAME = ''
MONGO_PASSWORD = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Kolkata'

DATE_FORMAT = '%d-%m-%Y'

SESSION_ENGINE = 'mongoengine.django.sessions'

SESSION_COOKIE_AGE = 60*60*24  #1 day  

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

LOGIN_URL = '/auth/login/'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR,'static')

UPLOAD_DIR  = os.path.join(MEDIA_ROOT,'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

ADMIN_THEME_URL = MEDIA_URL+'themes/admin/'

SITE_THEME_URL = MEDIA_URL+'themes/site/'

SITE_MEDIA_URL = MEDIA_URL+'site/'

DEFAULT_ADMIN_THEME = 'adminbluez'

DEFAULT_SITE_THEME = 'sitebluez'

DEFAULT_SITE = 'pantoto'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1p^wd@)ag@z9$40#q6-361(vzow@@rwrsn&(=5c*_2d#gpnpc)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'cms.conf.main_urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR,'templates'),
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'pantoto',
    'cms',
)


