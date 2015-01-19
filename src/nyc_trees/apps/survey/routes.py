# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import route, render_template

from apps.core.decorators import individual_mapper_do

from apps.survey import views as v
from apps.core.views import map_legend

#####################################
# RESERVATION ROUTES
#####################################

reserve_blockface_page = route(
    GET=individual_mapper_do(
        render_template('survey/reserve_blockface.html'),
        map_legend))

cancel_reservation = route(
    GET=individual_mapper_do(
        v.cancel_reservation))

edit_cart_for_blockface = individual_mapper_do(
    route(POST=v.add_blockface_to_cart,
          DELETE=v.remove_blockface_from_cart))

remove_blockface_from_cart = route(
    DELETE=individual_mapper_do(
        v.remove_blockface_from_cart))

reserve_blockfaces = individual_mapper_do(
    render_template('survey/blockface_cart.html'),
    route(POST=v.reserve_blockfaces,
          GET=v.blockface_cart_page))

blockface_reservations_confirmation_page = route(
    GET=individual_mapper_do(
        render_template('survey/reserve_blockface_confirmation.html'),
        v.blockface_reservations_confirmation_page))

#####################################
# SURVEY ROUTES
#####################################

survey = individual_mapper_do(
    route(GET=v.start_survey,
          POST=v.submit_survey))

choose_blockface_survey_page = route(
    GET=individual_mapper_do(
        v.choose_blockface_survey_page))

species_autocomplete_list = route(
    GET=v.species_autocomplete_list)

#####################################
# ADMIN ROUTES
#####################################

admin_blockface_page = route(
    GET=v.admin_blockface_page)

admin_blockface_partial = route(
    GET=v.admin_blockface_partial)

admin_blockface_detail_page = route(
    GET=v.admin_blockface_page)

admin_extend_blockface_reservation = route(
    POST=v.admin_extend_blockface_reservation)

admin_blockface_available = route(
    GET=v.admin_blockface_available)
