from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import flow_category as flow_category_api


@main.route("/v1/flow-categories/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_flow_categories():
    return flow_category_api.get_all_flow_categories()
