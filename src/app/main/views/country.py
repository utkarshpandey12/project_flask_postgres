from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import country as country_api


@main.route("/v1/countries/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_countries():
    return country_api.get_all_countries()


@main.route("/v1/countries/<int:country_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_country(country_id):
    return country_api.get_country(country_id)


@main.route("/v1/countries/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_country():
    return country_api.create_country(request.json)


@main.route("/v1/countries/<int:country_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_country(country_id):
    return country_api.delete_country(country_id, g.current_user)


@main.route("/v1/countries/<int:country_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_country(country_id):
    return country_api.update_country(country_id, request.json, g.current_user)
