# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.core.models import User
from apps.event.models import EventRegistration
from apps.users.models import achievements
from apps.users.forms import ProfileSettingsForm, EventRegistrationFormSet, \
    PrivacySettingsForm
from apps.survey.models import Tree


_FOLLOWED_GROUP_CHUNK_SIZE = 2


# TODO: make a route?
def user_detail_redirect(request):
    return HttpResponseRedirect(
        reverse('user_detail', kwargs={'username': request.user.username}))


def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    its_me = (user.id == request.user.id)

    if not its_me and not user.profile_is_public:
        # Private profile acts like a missing page to others
        raise Http404()

    return _user_profile_context(request, user, its_me)


def _get_follows_context(user):
    follows = user.follow_set.select_related('group').order_by('created_at')
    follows_count = follows.count()
    hidden_count = follows_count - _FOLLOWED_GROUP_CHUNK_SIZE

    return {
        'count': follows_count,
        'chunk_size': _FOLLOWED_GROUP_CHUNK_SIZE,
        'hidden_count': hidden_count,
        'follows': follows
    }


def _user_profile_context(request, user, its_me):
    user_achievements = set(user.achievement_set
                            .order_by('created_at')
                            .values_list('achievement_id', flat=True))

    block_count = user.survey_set.distinct('blockface').count()
    # TODO: This will count extra trees and species if a user surveys the
    #       same block twice.  We will likely have to write a raw query
    trees = Tree.objects.filter(survey__user=user)
    tree_count = trees.count()
    species_count = (trees
                     .filter(species__isnull=False)
                     .distinct('species')
                     .count())
    privacy_form = PrivacySettingsForm(instance=user)

    context = {
        'user': user,
        'viewing_own_profile': its_me,
        'show_username': ((its_me or user.real_name_is_public) and
                          (user.first_name or user.last_name)),
        'show_achievements': its_me or user.achievements_are_public,
        'show_contributions': its_me or user.contributions_are_public,
        'show_groups': its_me or user.group_follows_are_public,
        'show_individual_mapper': (user.individual_mapper and
                                   (its_me or user.profile_is_public)),
        'follows': _get_follows_context(user),
        'privacy_categories': _get_privacy_categories(privacy_form),
        'counts': {
            'block': block_count,
            'tree': tree_count,
            'species': species_count
        },
        'achievements': [achievements[key]
                         for key in user_achievements if key in achievements]
    }
    return context


def profile_settings(request):
    user = request.user
    privacy_form = PrivacySettingsForm(instance=user)
    profile_form = ProfileSettingsForm(instance=user, label_suffix='')
    profile_form.fields['opt_in_stewardship_info'].label = ''

    a_week_ago = timezone.now().date() - timedelta(days=7)
    events = EventRegistration.objects \
        .filter(event__begins_at__gt=a_week_ago) \
        .order_by('event__begins_at')
    event_formset = EventRegistrationFormSet(
        instance=user, queryset=events)

    context = {
        'profile_form': profile_form,
        'privacy_form': privacy_form,
        'event_formset': event_formset,
        'privacy_categories': _get_privacy_categories(privacy_form),
        'username': request.user.username,
    }
    return context


def _get_privacy_categories(form):
    user = form.instance

    def make_category(title, field_name):
        return {
            'title': title,
            'field_name': field_name,
            'is_public': getattr(user, field_name),
            'form_field': form[field_name]
        }

    return [
        make_category('Profile', 'profile_is_public'),
        make_category('Name', 'real_name_is_public'),
        make_category('Groups', 'group_follows_are_public'),
        make_category('Contributions', 'contributions_are_public'),
        make_category('Achievements', 'achievements_are_public'),
    ]


def update_profile_settings(request):
    user = request.user
    profile_form = ProfileSettingsForm(request.POST, instance=user)
    privacy_form = PrivacySettingsForm(request.POST, instance=user)
    event_formset = EventRegistrationFormSet(request.POST, instance=user)

    # It's not possible to create invalid data with this form,
    # so don't check form.is_valid()
    profile_form.save()
    privacy_form.save()
    event_formset.save()

    return profile_settings(request)


def set_privacy(request, username):
    user = request.user
    privacy_form = PrivacySettingsForm(request.POST, instance=user)
    privacy_form.save()
    return user_detail(request, username)


def update_user(request, username):
    # TODO: implement
    pass


def request_individual_mapper_status(request, username):
    # TODO: implement
    pass


def start_form_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_reservation_job(request, username):
    # TODO: implement
    pass


def start_map_for_tool_depots_job(request, username):
    # TODO: implement
    pass


def achievements_page(request):
    # TODO: implement
    return {}


def training_page(request):
    # TODO: implement
    return {}
