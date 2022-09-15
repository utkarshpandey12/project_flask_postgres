from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import user as user_api


@main.route("/v1/users/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_user():
    return user_api.create_user(request.json, g.current_user)


@main.route("/v1/users/<int:user_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_user(user_id):
    return user_api.update_user(user_id, request.json, g.current_user)


@main.route("/v1/users/<int:user_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_user(user_id):
    return user_api.get_user(user_id)


@main.route("/v1/users/", methods=["GET"])
@login_required
@sys_admin_required()
def get_users():
    return user_api.get_users()


@main.route("/v1/users/transcribers/", methods=["GET"])
@login_required
@sys_admin_required()
def get_transcriber_users():
    return user_api.get_transcriber_users()
