# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.forms import Form, BooleanField, CheckboxInput, EmailField
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from registration.forms import RegistrationFormUniqueEmail


class ForgotUsernameForm(Form):
    email = EmailField(label='Your email address')


class NycRegistrationForm(RegistrationFormUniqueEmail):
    tos = BooleanField(
        widget=CheckboxInput,
        label='I agree to the terms of use',
        error_messages={
            'required': 'You must agree to the terms to register'
        }
    )
    age_over_13 = BooleanField(
        widget=CheckboxInput,
        label='I am over 13 years old',
        required=False
    )


class UsernameOrEmailPasswordResetForm(forms.Form):
    '''
    Django 1.8 will expose an overridable ``get_users`` method
    that separates the filtering logic from the email sending
    logic. This is not available in 1.7, so the ``save`` method in
    this form was copied from
    https://github.com/django/django/blob/59fec1ca9b3c426466f0c613a5ecf2badb992460/django/contrib/auth/forms.py#L230-L276
    and slighly modified.
    '''
    email_or_username = forms.CharField(label="Email or Username",
                                        max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        email_or_username = self.cleaned_data["email_or_username"]
        for user in self.get_users(email_or_username):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, context)

            if html_email_template_name:
                html_email = loader.render_to_string(html_email_template_name,
                                                     context)
            else:
                html_email = None
            send_mail(subject, email, from_email, [user.email],
                      html_message=html_email)

    def get_users(self, email_or_username):
        matched_username_or_email_q = Q(email__iexact=email_or_username) | \
            Q(username__iexact=email_or_username)
        matched_and_active_q = Q(is_active=True) & matched_username_or_email_q

        active_users = get_user_model()._default_manager\
                                       .filter(matched_and_active_q)

        return (u for u in active_users if u.has_usable_password())
