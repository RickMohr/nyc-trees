# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.event.models import EventRegistration
from apps.users.views.user import USER_SETTINGS_PRIVACY_TAB_ID


def my_events_now(request):
    user = request.user
    if user.is_authenticated():
        registered_events = EventRegistration.my_events_now(user)
        attended_events, non_attended_events = registered_events
        all_current_events = attended_events + non_attended_events
        return {
            # Events user has not been checked-in to yet.
            'my_events_now': non_attended_events,
            # All upcoming and in-progress events.
            'my_events_now_all': all_current_events
        }
    return {}


def user_settings_privacy_url(request):
    base_url = reverse('user_profile_settings')
    full_url = '%s#%s' % (base_url, USER_SETTINGS_PRIVACY_TAB_ID)
    return {'user_settings_privacy_url': full_url}


def config(request):
    # At the time this function was written, the generated context was
    # only used in the base.html template, and our AJAX requests all
    # render partials, not full templates inheriting from base. Given
    # those constraints, we can skip generating this context, which
    # saves some database query time.
    if request.is_ajax():
        # The Django 1.7 docs say "Each context processor _must_ return
        # a dictionary."
        return {}

    return {
        'nyc_bounds': {
            'xmin': float(settings.NYC_BOUNDS[0]),
            'ymin': float(settings.NYC_BOUNDS[1]),
            'xmax': float(settings.NYC_BOUNDS[2]),
            'ymax': float(settings.NYC_BOUNDS[3])
        }
    }
