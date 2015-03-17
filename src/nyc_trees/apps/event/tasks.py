# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.files.base import ContentFile
from django.core.files.storage import DefaultStorage
from django.core.urlresolvers import reverse

from libs.phantomjs import url_to_pdf


def create_pdf_map(event):
    url = reverse('printable_event_map', kwargs={
        'group_slug': event.group.slug,
        'event_slug': event.slug,
        })
    pdf_bytes = url_to_pdf(url)

    content = ContentFile(pdf_bytes)

    # Will overwrite an existing file
    DefaultStorage.save(event.map_pdf_filename, content)
