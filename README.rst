==================
Django Text Office
==================

Django Text Office is a simple app to send and manage your text messages in
Django.

This is a clone project of Django Post Office but instead of sending e-mails it
sends text messages. Primary focus is on Short Messaging System (SMS)



Dependencies
============

* `django >= 1.8 <http://djangoproject.com/>`_


Installation
============

|Build Status|


* Install from PyPI (or you `manually download from PyPI <http://pypi.python.org/pypi/django-post_office>`_)::

    pip install django-post_office

* Add ``post_office`` to your INSTALLED_APPS in django's ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        # other apps
        "post_office",
    )

* Run ``migrate``::

    python manage.py migrate

* Set ``post_office.EmailBackend`` as your ``EMAIL_BACKEND`` in django's ``settings.py``::

    EMAIL_BACKEND = 'post_office.EmailBackend'


