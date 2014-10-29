# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models

from apps.core.models import User, Group


class Event(models.Model):
    # Once a group has events, we can't just delete the group, because
    # people could have registered to attend the group's events.
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    description = models.TextField(default='', blank=True)
    contact_email = models.EmailField(null=True)
    contact_info = models.TextField(default='', blank=True)
    begins_at =  models.DateTimeField()
    ends_at =  models.DateTimeField()
    location = models.PointField(srid=3857, db_column='the_geom_webmercator')
    max_attendees = models.IntegerField()
    includes_training = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    url_name = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EventRegistration(models.Model):
    user = models.ForeignKey(User)
    # If users have registered for an event, we do not want to allow
    # the event to be deleted. If we do, the registration will
    # disappear from the User's profile page and they may show up to
    # an event on the day, not knowing it was canceled
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    did_attend = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

