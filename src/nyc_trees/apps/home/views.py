# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from libs.sql import get_total_tree_count, get_total_species_count

from apps.core.models import User

from apps.event.event_list import immediate_events

from apps.home.training import training_summary

from apps.survey.models import Blockface, Survey

from apps.users import user_profile_context


def home_page(request):
    if request.user.is_authenticated():
        context = user_profile_context(request.user)
        context['training_steps'] = training_summary.get_context(request.user)
        context['counts_all'] = _global_counts()
        context['counts_week'] = _global_counts()
    else:
        context = {
            'user': request.user,
            'counts': _global_counts()
        }

    immediate_events_list = (immediate_events
                             .configure(chunk_size=3)
                             .as_context(request))

    context.update({'immediate_events': immediate_events_list})
    return context


def _global_counts():
    blocks_total = Blockface.objects.all().count()
    blocks_mapped = Survey.objects.all().distinct('blockface_id').count()
    if blocks_mapped > 0:
        blocks_percent = "{:.0%}".format(
            float(blocks_mapped) / float(blocks_total))
    else:
        blocks_percent = "0%"

    user_count = User.objects.filter(is_active=True).count()

    # In order to show the tree count in a "ticker" we need to break it up
    # into digits and pad it with zeroes.
    tree_count = get_total_tree_count()
    trees_digits = [digit for digit in "{:07d}".format(tree_count)]

    global_counts = {
        'species': get_total_species_count(),
        'tree': trees_digits,
        'block': blocks_mapped,
        'block_percent': blocks_percent,
        'user': user_count,
        'event': -999
        }
    return global_counts


def retrieve_job_status(request):
    # TODO: implement
    pass


def individual_mapper_instructions(request):
    pass


def about_faq_page(request):
    pass
