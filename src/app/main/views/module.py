from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import module as module_api


@main.route("/v1/modules/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_modules():
    return module_api.get_all_modules()
