# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import django.contrib.auth.views as contrib_auth

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django_tinsel.decorators import render_template
from django_tinsel.utils import decorate as do

from apps.core.models import User

from apps.login.forms import (ForgotUsernameForm,
                              UsernameOrEmailPasswordResetForm)


def logout(request):
    return contrib_auth.logout(request, next_page=reverse('home_page'))


def password_reset(request):
    return contrib_auth.password_reset(
        request,
        password_reset_form=UsernameOrEmailPasswordResetForm)


def forgot_username_page(request):
    if request.method == 'GET':
        form = ForgotUsernameForm()
    else:
        form = ForgotUsernameForm(request.REQUEST)

    return {'form': form}


def forgot_username(request):
    form = ForgotUsernameForm(request.POST)
    if not form.is_valid():
        return forgot_username_page_view(request)

    email = form.cleaned_data['email']
    users = User.objects.filter(email=email)

    # Don't reveal if we don't have that email, to prevent email harvesting
    if len(users) == 1:
        user = users[0]

        password_reset_url = request.build_absolute_uri(
            reverse('auth_password_reset'))

        subject = 'Account Recovery'
        body = render_to_string('login/forgot_username_email.txt',
                                {'user': user,
                                 'password_url': password_reset_url})

        user.email_user(subject, body, settings.DEFAULT_FROM_EMAIL)

    return {'email': email}


forgot_username_page_view = do(
    render_template('login/forgot_username.html'),
    forgot_username_page)

forgot_username_view = do(
    render_template('login/forgot_username_complete.html'),
    forgot_username)
