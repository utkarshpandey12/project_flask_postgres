from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import caller_id as caller_id_api


################################################################################
# Caller Ids
################################################################################
@main.route("/v1/caller-ids/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_caller_id():
    return caller_id_api.create_caller_id(request.json, g.current_user)


@main.route("/v1/caller-ids/<int:caller_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_caller_id(caller_id):
    return caller_id_api.update_caller_id(caller_id, request.json, g.current_user)


@main.route("/v1/caller-ids/<int:caller_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_caller_id(caller_id):
    return caller_id_api.delete_caller_id(caller_id, g.current_user)


@main.route("/v1/caller-ids/", methods=["GET"])
@login_required
@sys_admin_required()
def get_caller_ids():
    return caller_id_api.get_caller_ids()


@main.route("/v1/caller-ids/<int:caller_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_caller_id(caller_id):
    return caller_id_api.get_caller_id(caller_id)


################################################################################
# Org Caller Ids
################################################################################
@main.route("/v1/orgs/<int:org_id>/caller-ids/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_org_caller_id(org_id):
    return caller_id_api.create_org_caller_id(org_id, request.json, g.current_user)


@main.route("/v1/orgs/<int:org_id>/caller-ids/<int:caller_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_org_caller_id(org_id, caller_id):
    return caller_id_api.update_org_caller_id(
        org_id, caller_id, request.json, g.current_user
    )


@main.route("/v1/orgs/<int:org_id>/caller-ids/<int:caller_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_org_caller_id(org_id, caller_id):
    return caller_id_api.delete_org_caller_id(org_id, caller_id, g.current_user)


@main.route("/v1/orgs/<int:org_id>/caller-ids/", methods=["GET"])
@login_required
@sys_admin_required()
def get_org_caller_ids(org_id):
    return caller_id_api.get_org_caller_ids(org_id)


@main.route("/v1/orgs/<int:org_id>/caller-ids/<int:caller_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_org_caller_id(org_id, caller_id):
    return caller_id_api.get_org_caller_id(org_id, caller_id)
