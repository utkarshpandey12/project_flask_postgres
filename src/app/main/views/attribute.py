from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import attribute as attribute_api


@main.route("/v1/attributes/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_attributes():
    return attribute_api.get_all_attributes()
