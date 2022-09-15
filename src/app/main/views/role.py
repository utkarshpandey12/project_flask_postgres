from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import role as role_api


@main.route("/v1/roles/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_roles():
    return role_api.get_all_roles()


@main.route("/v1/roles/<int:role_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_role(role_id):
    return role_api.get_role(role_id)


@main.route("/v1/roles/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_role():
    return role_api.create_role(request.json, g.current_user)


@main.route("/v1/roles/<int:role_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_role(role_id):
    return role_api.delete_role(role_id, g.current_user)


@main.route("/v1/roles/<int:role_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_role(role_id):
    return role_api.update_role(role_id, request.json, g.current_user)


@main.route("/v1/orgs/<int:org_id>/roles/", methods=["GET"])
@login_required
@sys_admin_required()
def get_org_roles(org_id):
    return role_api.get_org_roles(org_id)
