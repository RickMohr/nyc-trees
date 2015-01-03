# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core import mail

from apps.core.test_utils import make_request, make_event

from apps.users.tests import UsersTestCase

from apps.event.models import EventRegistration
from apps.event.views import events_list_page, event_email


class EventTestCase(UsersTestCase):
    def setUp(self):
        super(EventTestCase, self).setUp()
        self.event = make_event(self.group)


class EventListTest(EventTestCase):
    def test_following_user(self):
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertFalse(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_following_user_registered(self):
        EventRegistration.objects.create(user=self.user,
                                         event=self.event)
        request = make_request(user=self.user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 1)
        self.assertTrue(
            ctx['immediate_events']['event_infos'][0]['user_is_registered'])

    def test_other_user(self):
        request = make_request(user=self.other_user)
        ctx = events_list_page(request)
        self.assertEqual(len(ctx['all_events']['event_infos']), 1)
        self.assertEqual(len(ctx['immediate_events']['event_infos']), 0)
        self.assertFalse(
            ctx['all_events']['event_infos'][0]['user_is_registered'])


class EventEmailTest(EventTestCase):
    def test_sending_email(self):
        reg = EventRegistration(event=self.event, user=self.user)
        reg.clean_and_save()

        request = make_request({
            'subject': 'Come to the event',
            'body': "It's happening now!"
        }, self.other_user, 'POST', group=self.group)

        context = event_email(request, self.event.slug)

        self.assertEqual(mail.outbox[0].subject, "Come to the event")
        self.assertTrue(context['message_sent'])
        self.assertEqual(self.event, context['event'])
        self.assertEqual(self.group, context['group'])

        # Clear the test inbox
        mail.outbox = []
