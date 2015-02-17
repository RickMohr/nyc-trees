# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from apps.home.training import training_summary
from apps.users import user_profile_context
from apps.event.event_list import immediate_events


def home_page(request):
    if request.user.is_authenticated():
        context = user_profile_context(request.user, True)
        context['training_steps'] = training_summary.get_context(request.user)
    else:
        context = {'user': request.user}

    immediate_events_list = (immediate_events
                             .configure(chunk_size=3)
                             .as_context(request))

    context.update({'immediate_events': immediate_events_list})
    return context


def retrieve_job_status(request):
    # TODO: implement
    pass


def individual_mapper_instructions(request):
    pass
