# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from urlparse import urljoin

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from celery import task

from apps.core.models import User
from apps.mail import MessageType
from apps.mail.libs import send_to, storage_pdf_to_attachment
from apps.survey.models import Blockface, BlockfaceReservation
from apps.event.models import Event


@task
def notify_reservation_confirmed(pdf_filename, user_id, reservation_ids):
    if not reservation_ids:
        # Return some meaningful log output for this celery task.
        return {
            'user_id': user_id,
            'success': False,
            'message': 'No new reservations to confirm'
        }

    user = User.objects.get(id=user_id)
    reservations = BlockfaceReservation.objects.filter(id__in=reservation_ids)
    blockface_ids = reservations.values_list('blockface_id', flat=True)
    blockfaces = Blockface.objects.filter(id__in=blockface_ids)
    expiration_date = reservations[0].expires_at
    if pdf_filename:
        attachments = [storage_pdf_to_attachment(pdf_filename)]
    else:
        attachments = None

    root_url = 'http://%s' % Site.objects.get_current().domain
    reservations_url = urljoin(root_url, reverse('reservations'))

    return send_to(user,
                   MessageType.NEW_RESERVATIONS_CONFIRMED,
                   blockfaces=blockfaces,
                   reservations_url=reservations_url,
                   expiration_date=expiration_date,
                   attachments=attachments)


@task
def notify_rsvp(pdf_filename, absolute_event_url, user_id, event_id):
    user = User.objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)
    if pdf_filename:
        attachments = [storage_pdf_to_attachment(pdf_filename)]
    else:
        attachments = None

    return send_to(user,
                   MessageType.RSVP,
                   event=event,
                   event_url=absolute_event_url,
                   attachments=attachments)
