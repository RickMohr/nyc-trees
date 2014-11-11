# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^', include('apps.home.urls')),
    url(r'^login/', include('apps.login.urls')),
    url(r'^blockface/', include('apps.survey.urls.blockface')),
    url(r'^census_admin/', include('apps.census_admin.urls')),
    url(r'^census_admin/', include('apps.survey.urls.census_admin')),
    url(r'^event/', include('apps.event.urls.event')),
    url(r'^group/', include('apps.event.urls.group')),
    url(r'^group/', include('apps.users.urls.group')),
    url(r'^quiz/', include('apps.achievement.urls')),
    url(r'^species/', include('apps.survey.urls.species')),
    url(r'^survey/', include('apps.survey.urls.survey')),
    url(r'^user/', include('apps.users.urls.user')),
)
