from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import sender_id as sender_id_api


@main.route("/v1/orgs/<int:org_id>/sender-ids/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_sender_id(org_id):
    return sender_id_api.create_sender_id(org_id, request.json, g.current_user)


@main.route("/v1/orgs/<int:org_id>/sender-ids/<int:sender_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_sender_id(org_id, sender_id):
    return sender_id_api.update_sender_id(
        org_id, sender_id, request.json, g.current_user
    )


@main.route("/v1/orgs/<int:org_id>/sender-ids/<int:sender_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_sender_id(org_id, sender_id):
    return sender_id_api.delete_sender_id(org_id, sender_id, g.current_user)


@main.route("/v1/orgs/<int:org_id>/sender-ids/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_sender_ids(org_id):
    return sender_id_api.get_all_sender_ids(org_id)


@main.route("/v1/orgs/<int:org_id>/sender-ids/<int:sender_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_sender_id(org_id, sender_id):
    return sender_id_api.get_sender_id(org_id, sender_id)
