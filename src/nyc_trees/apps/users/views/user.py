# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django_tinsel.decorators import render_template
from django_tinsel.utils import decorate as do

from apps.core.models import User
from apps.users.forms import ProfileSettingsForm


def user_detail_redirect(request):
    return HttpResponseRedirect(
        reverse('user_detail', kwargs={'username': request.user.username}))


def user_profile_context(request, username):
    user = get_object_or_404(User, username=username)
    its_me = (user.id == request.user.id)

    if not its_me and not user.profile_is_public:
        # Private profile acts like a missing page to others
        raise Http404()

    context = {
        'user': user,
        'viewing_own_profile': its_me,
        'show_username': ((its_me or user.real_name_is_public) and
                          (user.first_name or user.last_name)),
        'show_achievements': its_me or user.achievements_are_public,
        'show_contributions': its_me or user.contributions_are_public,
        'show_groups': its_me or user.group_follows_are_public,
        'show_individual_mapper': (user.individual_mapper and
                                   (its_me or user.profile_is_public))
    }
    return render_to_response('users/profile.html', context,
                              RequestContext(request))


def profile_settings_context(request):
    form = ProfileSettingsForm(instance=request.user, label_suffix='')
    form.fields['opt_in_events_info'].label = 'Yes'
    form.fields['opt_in_stewardship_info'].label = 'Yes'

    context = {
        'form': form,
        'privacy_categories': _get_privacy_categories(form),
        'username': request.user.username,
    }
    return context


def _get_privacy_categories(form):
    user = form.instance
    return [
        {
            'title': 'Profile',
            'is_public': user.profile_is_public,
            'form_field': form['profile_is_public']
        }, {
            'title': 'Groups',
            'is_public': user.group_follows_are_public,
            'form_field': form['group_follows_are_public']
        }, {
            'title': 'Contributions',
            'is_public': user.contributions_are_public,
            'form_field': form['contributions_are_public']
        }, {
            'title': 'Achievements',
            'is_public': user.achievements_are_public,
            'form_field': form['achievements_are_public']
        }
    ]


def update_profile_settings_view(request):
    form = ProfileSettingsForm(request.POST, instance=request.user)
    # It's not possible to create invalid data with this form,
    # so don't check form.is_valid()
    form.save()
    return user_profile_context(request, request.user.username)


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


user_detail = do(
    render_template('users/profile.html'),
    user_profile_context)

user_settings = do(
    render_template('users/settings.html'),
    profile_settings_context)

update_profile_settings = do(
    render_template('users/profile.html'),
    update_profile_settings_view)
