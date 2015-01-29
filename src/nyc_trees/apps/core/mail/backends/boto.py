# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json
import logging
import sys
import traceback

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from django_statsd.clients import statsd

from libs.boto_mailer import BotoMailer

logger = logging.getLogger(__name__)


class EmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, aws_region='us-east-1'):
        super(EmailBackend, self).__init__(fail_silently=fail_silently)
        self.mailer = BotoMailer(aws_region)
        self.check_quota = getattr(settings, 'EMAIL_BOTO_CHECK_QUOTA', False)

    def send_messages(self, email_messages):
        if not email_messages:
            return
        sent_message_count = 0

        if self.check_quota:
            remaining_quota = self.mailer.get_remaining_message_quota()
            self._log_quota(remaining_quota)
        else:
            remaining_quota = sys.maxint

        if len(email_messages) <= remaining_quota:
            for email_message in email_messages:
                if self._send_message(email_message):
                    sent_message_count += 1
            return sent_message_count
        else:
            raise SESQuotaException("Attempted to send %d messages with only "
                                    "%d remaining. Wait before retrying" %
                                    (len(email_messages), remaining_quota),
                                    email_messages)

    def _send_message(self, email_message):
        message = email_message.message()
        try:
            response = self.mailer.send_message_bytes(
                message.as_bytes(linesep='\r\n'),
                email_message.from_email,
                email_message.to)
            self._log_message(email_message, response)
            return response
        except Exception:
            self._log_message_failure(email_message,
                                      traceback.format_exc())
            if not self.fail_silently:
                raise

    def _log_message(self, email_message, response):
        statsd.incr('email.message.success')
        logger.debug('Sent email with subject "%s" to %s: %s' % (
            email_message.subject, email_message.to, json.dumps(response)))

    def _log_message_failure(self, email_message, trace):
        statsd.incr('email.message.failure')
        logger.error('Exception raised while sending email '
                     'with subject "%s" to %s: %s' % (
                         email_message.subject, email_message.to, trace))

    def _log_quota(self, quota):
        statsd.gauge('email.quota', quota)


class SESQuotaException(Exception):
    def __init__(self, message, email_messages):
        super(Exception, self).__init__(message)
        self.email_messages = email_messages
