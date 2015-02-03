# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.auth.decorators import login_required

from django_tinsel.utils import decorate as do
from django_tinsel.decorators import route, render_template

from apps.login import views as v
from apps.login.backends import NycRegistrationView


#####################################
# ACCOUNTS ROUTES
#####################################

logout = do(v.logout)
password_reset = do(v.password_reset)

activation_complete = do(
    login_required,
    render_template('registration/activation_complete.html'),
    route(GET=v.activation_complete,
          POST=v.save_optional_info))

register = NycRegistrationView.as_view()

#####################################
# LOGIN ROUTES
#####################################

forgot_username = do(
    render_template('login/forgot_username.html'),
    route(GET=v.forgot_username_page, POST=v.forgot_username))

forgot_username_sent = do(
    render_template('login/forgot_username_complete.html'),
    v.forgot_username_sent)
