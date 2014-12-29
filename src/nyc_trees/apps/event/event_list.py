# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from collections import OrderedDict

from urllib import urlencode
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from apps.users.models import Follow
from apps.event.models import Event, EventRegistration


_ALL, _MAPPING, _TRAINING = 'all', 'mapping', 'training'


class _Filters(object):
    ALL = _ALL
    MAPPING = _MAPPING
    TRAINING = _TRAINING


class EventList(object):
    """
    Wrap a queryset building function into a workflow that supports
    rendering into pages and reloading asychronously using endpoints
    that return markup.
    """
    trainingFilters = 'training_filter'
    Filters = _Filters

    @staticmethod
    def get_filterset(name):
        filtersets = {
            EventList.trainingFilters: OrderedDict([
                (_ALL, None),
                (_MAPPING, lambda qs: qs.filter(includes_training=False)),
                (_TRAINING, lambda qs: qs.filter(includes_training=True)),
            ]),
        }
        return filtersets.get(name, {})

    @staticmethod
    def simple_context(request, qs):
        """
        Render an Event queryset as an event_list context.

        Useful for cases where you don't need post-back controls and
        don't want to bother creating an EventList instance.
        """
        return {'event_infos': EventList.make_event_infos(request, qs),
                'filters': None,
                'load_more_url': None}

    @staticmethod
    def make_event_infos(request, qs):
        """
        Wrap an event object with user-aware data necessary for
        rendering an event row.
        """
        user_registered_event_ids = set(EventRegistration.objects
                                        .filter(user_id=request.user.pk)
                                        .values_list('event_id', flat=True))

        return [{'event': event,
                 'user_is_registered': event.pk in user_registered_event_ids}
                for event in qs]

    #########################################
    # instance and type configuration
    #########################################

    def __init__(self, qs_builder,
                 template_path='event/partials/event_list.html',
                 chunk_size=None, active_filter=None, filterset_name=None):

        object.__setattr__(self, 'name', qs_builder.__code__.co_name)
        object.__setattr__(self, 'qs_builder', qs_builder)
        object.__setattr__(self, 'template_path', template_path)

        object.__setattr__(self, 'chunk_size', chunk_size)
        object.__setattr__(self, 'active_filter', active_filter)
        object.__setattr__(self, 'filterset_name', filterset_name)

    def __setattr__(self, *args, **kwargs):
        raise TypeError("Mutating this object is too risky because it "
                        "most likely lives the entire length of a thread. "
                        "most needs can be met with `.configure`")

    def configure(self, **kwargs):
        """
        Customize the configuration of an event list for presentation
        on a page.

        Returns a new EventList objects with modified settings.

        This is necessary if the default state of the EventList was
        constructed in some way other than how you intend to present
        it. For example, if the default state of 'foo_events' is a
        chunk_size of 4, but you want to show them all, you can
        specify this with `foo_events.configure(chunk_size=4)`. This
        will prevent mutation of the event list in other cases, but
        allow you to render it with your preferred initial
        presentation.
        """
        # preprocess chunk_size because this is sometimes
        # configured directly from an HTTP request dict.
        if 'chunk_size' in kwargs:
            chunk_size = kwargs['chunk_size']
            if chunk_size is None or chunk_size == 'None':
                chunk_size = None
            else:
                chunk_size = int(chunk_size)
            kwargs['chunk_size'] = chunk_size

        newkwargs = {key: (kwargs[key] if key in kwargs
                           else getattr(self, key))
                     for key in
                     ('chunk_size', 'active_filter', 'filterset_name')}
        return EventList(self.qs_builder, **newkwargs)

    def __call__(self, *args, **kwargs):
        """
        Call the wrapped function directly, returning a queryset.
        """
        return self.qs_builder(*args, **kwargs)

    def _get_active_filter_fn(self):
        return (self
                .get_filterset(self.filterset_name)
                .get(self.active_filter))

    #########################################
    # methods for exposing url endpoints
    #########################################

    def url_name(self):
        return self.name + '_partial'

    def endpoint(self, *args, **kwargs):
        """
        The endpoint used to render a partial.
        """
        return render_to_response(
            self.template_path,
            {'event_list': self.as_context(*args, **kwargs)})

    #########################################
    # event list control management
    #########################################

    def _control_url(self, show_all, *args, **kwargs):
        params = {
            'chunk_size': self.chunk_size,
            'active_filter': self.active_filter,
            'filterset_name': self.filterset_name
        }

        if show_all:
            params['show_all'] = True
        url = reverse(self.url_name(), args=args, kwargs=kwargs)
        return '%s?%s' % (url, urlencode(params))

    def as_context(self, request, *args, **kwargs):
        qs = self.qs_builder(request, *args, **kwargs)
        event_list = self.configure(**request.GET.dict())

        filter_fn = event_list._get_active_filter_fn()
        if filter_fn:
            qs = filter_fn(qs)

        if ((request.GET.get('show_all') or
             event_list.chunk_size is None or
             qs.count() <= event_list.chunk_size)):
            load_more_url = None
        else:
            qs = qs[:event_list.chunk_size]
            load_more_url = event_list._control_url(
                show_all=True, *args, **kwargs)

        filterset = event_list.get_filterset(event_list.filterset_name)
        filters = ([{'name': k,
                     'active': k == event_list.active_filter,
                     'url': (event_list
                             .configure(active_filter=k)
                             ._control_url(show_all=False, *args, **kwargs))}
                    for k in filterset])

        return {
            'filters': filters,
            'load_more_url': load_more_url,
            'event_infos': event_list.make_event_infos(request, qs),
        }


#########################################
# event_list functions
#########################################
#
# Add your event_list constructors here.
#
# Write a function that takes a request and returns a
# queryset. Decorate it with `@EventList` and it is ready to be used
# as an endpoint for rendering a partial, or a context for use in a
# page delivered by the server.
#

@EventList
def immediate_events(request):
    user = request.user
    seven_days = relativedelta(days=7)
    nowish = (Event.objects
              .filter(is_private=False,
                      begins_at__gte=now() - seven_days,
                      begins_at__lte=now() + seven_days)
              .order_by('begins_at'))

    if user.is_authenticated():
        follows = Follow.objects.filter(user_id=user.id)
        groups = follows.values_list('group', flat=True)
        immediate_events = nowish.filter(group_id__in=groups)
    else:
        immediate_events = nowish.none()

    return immediate_events


@EventList
def all_events(request):
    return Event.objects.filter(is_private=False).order_by('begins_at')
