# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django_tinsel.decorators import render_template


def cancel_reservation(request, blockface_id):
    # TODO: implement
    pass


def add_blockface_to_cart(request, blockface_id):
    # TODO: implement
    pass


def remove_blockface_from_cart(request, blockface_id):
    # TODO: implement
    pass


@render_template('survey/blockface_cart.html')
def blockface_cart_page(request):
    # TODO: implement
    return {}


def reserve_blockfaces(request):
    # TODO: implement
    pass


@render_template('survey/reserve_blockface_confirmation.html')
def blockface_reservations_confirmation_page(request):
    # TODO: implement
    return {}


def start_survey(request, blockface_id):
    # TODO: implement
    pass


def submit_survey(request, blockface_id):
    # TODO: implement
    pass


def choose_blockface_survey_page(request):
    # TODO: implement
    pass


def species_autocomplete_list(request):
    # TODO: implement
    pass


def admin_blockface_page(request):
    # TODO: implement
    pass


def admin_blockface_partial(request):
    # TODO: implement
    pass


def admin_blockface_detail_page(request, blockface_id):
    # TODO: implement
    pass


def admin_extend_blockface_reservation(request, blockface_id):
    # TODO: implement
    pass


def admin_blockface_available(request, blockface_id):
    # TODO: implement
    pass
