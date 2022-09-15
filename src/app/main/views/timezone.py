from flask import request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import timezone as timezone_api


@main.route("/v1/timezones/", methods=["GET"])
@login_required
@sys_admin_required()
def get_timezone():
    return timezone_api.get_all_timezones()


@main.route("/v1/timezones/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_timezone():
    return timezone_api.create_timezone(request.json)
