# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import patterns, url

from django_tinsel.decorators import route

from apps.core.decorators import census_admin_do
from apps.census_admin.views import (start_admin_users_job,
                                     start_admin_surveys_job, admin_edits_page,
                                     admin_edits_partial,
                                     admin_training_material_list,
                                     admin_training_material)


# These URLs have the prefix 'census_admin/'
urlpatterns = patterns(
    '',
    url(r'^users-export/$',
        census_admin_do(route(POST=start_admin_users_job)),
        name='start_admin_users_job'),

    url(r'^surveys-export/$',
        census_admin_do(route(POST=start_admin_surveys_job)),
        name='start_admin_surveys_job'),

    url(r'^edits/$',
        census_admin_do(route(GET=admin_edits_page)),
        name='admin_edits_page'),

    url(r'^edits-partial/$',
        census_admin_do(route(GET=admin_edits_partial)),
        name='admin_edits_partial'),

    # TODO: Use Django flatpages for training POST/PUT endpoints

    url(r'^training/$',
        census_admin_do(route(GET=admin_training_material_list,
                              # POST=add_training_material
        )),
        name='admin_training_material_list'),

    url(r'^training/(?P<training_material_url_name>\w+)/$',
        census_admin_do(route(GET=admin_training_material,
                              # PUT=edit_training_material
        )),
        name='admin_training_material'),

    # TODO: Verify that these are provided by the django admin, then delete
    #
    # url(r'^admin/users/(?P<username>\w+)/individual-mapper-request/$', census_admin(route(POST=confirm_individual_mapper, DELETE=deny_individual_mapper))),  # NOQA
    # url(r'^admin/users/individual-mapper-requests/$', census_admin(route(GET=individual_mapper_requests_page))),  # NOQA
    # url(r'^admin/group/(?P<group_name>\w+)/$', census_admin(route(GET=admin_group_detail, PUT=admin_update_group))),  # admin_update_group includes editing blockface reservations and setting admin  # NOQA
    # url(r'^admin/group/(?P<group_name>\w+)/enable/$', census_admin(route(POST=enable_group))),  # NOQA
    # url(r'^admin/group/(?P<group_name>\w+)/disable/$', census_admin(route(POST=disable_group))),  # NOQA
)
