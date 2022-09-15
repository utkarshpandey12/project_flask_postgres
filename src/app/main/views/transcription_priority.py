from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import transcription_priority as transcription_priority_api


@main.route("/v1/transcription-priorities/", methods=["GET"])
@login_required
@sys_admin_required()
def get_transcription_priorities():
    return transcription_priority_api.get_transcription_priorities()


@main.route(
    "/v1/transcription-priorities/<int:transcription_priority_id>/", methods=["GET"]
)
@login_required
@sys_admin_required()
def get_transcription_priority(transcription_priority_id):
    return transcription_priority_api.get_transcription_priority(
        transcription_priority_id
    )


@main.route("/v1/transcription-priorities/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_transcription_priority():
    return transcription_priority_api.create_transcription_priority(
        request.json, g.current_user
    )


@main.route(
    "/v1/transcription-priorities/<int:transcription_priority_id>/", methods=["PUT"]
)
@login_required
@sys_admin_required()
@transaction()
def update_transcription_priority(transcription_priority_id):
    return transcription_priority_api.update_transcription_priority(
        transcription_priority_id, request.json, g.current_user
    )


@main.route(
    "/v1/transcription-priorities/<int:transcription_priority_id>/", methods=["DELETE"]
)
@login_required
@sys_admin_required()
@transaction()
def delete_transcription_priority(transcription_priority_id):
    return transcription_priority_api.delete_transcription_priority(
        transcription_priority_id, g.current_user
    )
