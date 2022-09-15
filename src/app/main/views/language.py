from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import language as language_api


@main.route("/v1/languages/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_languages():
    return language_api.get_all_languages()


@main.route("/v1/languages/<int:language_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_language(language_id):
    return language_api.get_language(language_id)


@main.route("/v1/languages/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_language():
    return language_api.create_language(request.json, g.current_user)


@main.route("/v1/languages/<int:language_id>/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_language(language_id):
    return language_api.update_language(language_id, request.json, g.current_user)


@main.route("/v1/languages/<int:language_id>/", methods=["DELETE"])
@login_required
@sys_admin_required()
@transaction()
def delete_language(language_id):
    return language_api.delete_language(language_id, g.current_user)
