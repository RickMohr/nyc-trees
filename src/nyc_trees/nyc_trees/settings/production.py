"""Production settings and globals."""


from os import environ
from urllib2 import urlopen, URLError

from base import *  # NOQA

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

# HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production  # NOQA
ALLOWED_HOSTS = [
    'treescount.nycgovparks.org',
    'treescount.azavea.com',
    '.elb.amazonaws.com',
    'localhost'
]

# ELBs use the instance IP in the Host header and ALLOWED_HOSTS checks against
# the Host header.
try:
    ALLOWED_HOSTS.append(
        urlopen(
            'http://instance-data.ec2.internal/latest/meta-data/local-ipv4'
        ).readline()
    )
except URLError:
    pass
# END HOST CONFIGURATION

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'apps.core.mail.backends.boto.EmailBackend'
# END EMAIL CONFIGURATION


# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# END CACHE CONFIGURATION


# SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('DJANGO_SECRET_KEY')
# END SECRET CONFIGURATION
