# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

TESTS_REQUIRE = ['tox >= 2.3', 'celery >=3.1, <4.0']

setup(
    name='django-text_office',
    version='0.1.0',
    author=u'Piotr Kaczyński',
    author_email='pkaczyns@gmail.com',
    packages=find_packages(),
    url='https://github.com/ui/django-text_office',
    license='MIT',
    description='A Django app to monitor and send text messages '
                'asynchronously, complete with template support.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.rst']},
    install_requires=[
        'django>=1.8', 'django-jsonfield>=1.0', 'django-sendsms',
        'six>=1.10', 'django-phonenumber-field>=1.1',
        'django-jsonfield >= 1.0, < 1.1'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    tests_require=TESTS_REQUIRE,
    extras_require={
        'test': TESTS_REQUIRE,
    },
)
