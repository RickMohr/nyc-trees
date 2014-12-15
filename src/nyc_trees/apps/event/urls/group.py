# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from apps.event.routes import (events, add_event, event_detail,
                               event_edit, event_popup_partial,
                               event_registration, start_event_map_print_job,
                               event_check_in_page, event_check_in,
                               email_event_registered_users)

# These URLs have the prefix 'group/'
urlpatterns = patterns(
    '',
    url(r'^(?P<group_slug>[\w-]+)/event/$',
        events, name='events'),

    url(r'^(?P<group_slug>[\w-]+)/add-event/$',
        add_event, name='add_event'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/$',
        event_detail, name='event_detail'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/edit/$',
        event_edit, name='event_edit'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/popup/$',
        event_popup_partial, name='event_popup_partial'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/register/$',
        event_registration, name='event_registration'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/printable-map/$',
        start_event_map_print_job, name='start_event_map_print_job'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/checkin/$',
        event_check_in_page, name='event_check_in_page'),

    url(r'^(?P<group_slug>[\w-]+)/event/'
        r'(?P<event_slug>[\w-]+)/checkin/(?P<username>[^/]+)/$',
        event_check_in, name='event_check_in'),

    url(r'^(?P<group_slug>[\w-]+)/event/(?P<event_slug>[\w-]+)/email/$',
        email_event_registered_users, name='email_event_registered_users'),
)
