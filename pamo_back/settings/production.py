from .base import *
from decouple import config

print('\n\n\n*********************************PRODUCCION**********************\n\n\n\n')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

CORS_ALLOWED_ORIGINS =[
   'https://*.pamofront-nexuspamo.up.railway.app',
   'pamofront-nexuspamo.up.railway.app'
]

ALLOWED_HOSTS = ['https://*.pamofront-nexuspamo.up.railway.app','pamofront-nexuspamo.up.railway.app', 'pamoback-nexuspamo.up.railway.app']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('NAME'),
        'USER': config('USER'),
        'PASSWORD': config('PASSWORD'),
        'HOST': config('HOST'),
        'PORT': config('PORT'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"