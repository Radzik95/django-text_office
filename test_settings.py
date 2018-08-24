# -*- coding: utf-8 -*-
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'text_office',
)

SECRET_KEY = 'ihavenosecrets'

ROOT_URLCONF = 'test_settings'

urlpatterns = []

MIDDLEWARE_CLASSES = (
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
            ],
        },
    },
]

LOGGING = {}

# Fix for missing SKIP_SOUTH_MIGRATIONS
# see https://gist.github.com/NotSqrt/5f3c76cd15e40ef62d09
class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = {
    'text_office': None,
}