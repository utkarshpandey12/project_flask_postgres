from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import org as org_api


@main.route("/v1/orgs/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_org():
    return org_api.create_org(request.json, g.current_user)


@main.route("/v1/orgs/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_orgs():
    return org_api.get_all_orgs()


@main.route("/v1/orgs/<int:org_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_org_details(org_id):
    return org_api.get_org_details(org_id)


@main.route("/v1/orgs/<int:org_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_org(org_id):
    return org_api.update_org(org_id, request.json, g.current_user)


@main.route("/v1/orgs/<int:org_id>/users/", methods=["GET"])
@login_required
@sys_admin_required()
def get_org_user_details(org_id):
    return org_api.get_org_user_details(org_id)
