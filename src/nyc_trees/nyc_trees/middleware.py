# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import re
import waffle

from django.conf import settings
from django.shortcuts import redirect


class SoftLaunchMiddleware(object):
    def __init__(self):
        self.redirect_url = getattr(settings, 'SOFT_LAUNCH_REDIRECT_URL', '/')
        regexes = getattr(settings, 'SOFT_LAUNCH_REGEXES', [])
        self.regexes = [re.compile(r) for r in regexes]

    def process_view(self, request, view_func, view_args, view_kwargs):
        if waffle.flag_is_active(request, 'full_access'):
            return None

        allowed = ((request.path == self.redirect_url) or
                   any(r.match(request.path) for r in self.regexes))

        if not allowed:
            return redirect(self.redirect_url)
