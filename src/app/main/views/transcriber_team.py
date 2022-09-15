from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import transcriber_team as transcriber_team_api


@main.route("/v1/transcriber-teams/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_transcriber_team():
    return transcriber_team_api.create_transcriber_team(request.json, g.current_user)


@main.route("/v1/transcriber-teams/<int:transcriber_team_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_transcriber_team(transcriber_team_id):
    return transcriber_team_api.update_transcriber_team(
        transcriber_team_id, request.json, g.current_user
    )


@main.route(
    "/v1/transcriber-teams/<int:transcriber_team_id>/transcribers/", methods=["POST"]
)
@login_required
@sys_admin_required()
@transaction()
def add_transcriber(transcriber_team_id):
    return transcriber_team_api.add_transcriber(
        transcriber_team_id, request.json, g.current_user
    )


@main.route(
    "/v1/transcriber-teams/<int:transcriber_team_id>/transcribers/<int:user_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_transcriber(transcriber_team_id, user_id):
    return transcriber_team_api.delete_transcriber(
        transcriber_team_id, user_id, g.current_user
    )


@main.route(
    "/v1/transcriber-teams/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_transcriber_teams():
    return transcriber_team_api.get_transcriber_teams()


@main.route(
    "/v1/transcriber-teams/<int:transcriber_team_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_transcriber_team(transcriber_team_id):
    return transcriber_team_api.get_transcriber_team(transcriber_team_id)


@main.route("/v1/transcriber-team-orgs/", methods=["GET"])
@login_required
@sys_admin_required()
def get_transcriber_team_orgs():
    return transcriber_team_api.get_transcriber_team_orgs()


@main.route("/v1/transcriber-team-orgs/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def add_transcriber_team_org():
    return transcriber_team_api.add_transcriber_team_org(request.json, g.current_user)


@main.route(
    "/v1/transcriber-team-orgs/<int:transcriber_team_org_id>/", methods=["DELETE"]
)
@login_required
@sys_admin_required()
@transaction()
def delete_transcriber_team_org(transcriber_team_org_id):
    return transcriber_team_api.delete_transcriber_team_org(
        transcriber_team_org_id, g.current_user
    )
