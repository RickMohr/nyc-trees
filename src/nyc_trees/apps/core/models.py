# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError


class User(AbstractUser):
    online_training_complete = models.BooleanField(default=False)
    individual_mapper = models.BooleanField(default=False)
    requested_individual_mapping_at = models.DateTimeField(null=True,
                                                           blank=True)

    profile_is_public = models.BooleanField(default=False)
    real_name_is_public = models.BooleanField(default=False)
    group_follows_are_public = models.BooleanField(default=False)
    contributions_are_public = models.BooleanField(default=False)
    achievements_are_public = models.BooleanField(default=False)

    is_flagged = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    is_census_admin = models.BooleanField(default=False)
    is_ambassador = models.BooleanField(default=False)
    is_minor = models.BooleanField(default=False)

    opt_in_events_info = models.BooleanField(default=False)
    opt_in_stewardship_info = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def clean(self):
        if ((User.objects.exclude(pk=self.pk)
             .filter(email__iexact=self.email).exists())):
            raise ValidationError({'email': [
                'This email address is already in use. '
                'Please supply a different email address.']
            })

        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(User, self).save(*args, **kwargs)


class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='', blank=True)
    contact_info = models.TextField(default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_url = models.URLField(null=True)
    # Deleting a user should not cascade delete the group of which
    # they are an admin. A new admin should be set before a user
    # delete is allowed.
    admin = models.ForeignKey(User, on_delete=models.PROTECT)
    image = models.ImageField(null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
