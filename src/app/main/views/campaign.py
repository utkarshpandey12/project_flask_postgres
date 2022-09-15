from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import campaign as campaign_api


@main.route("/v1/campaigns/search/", methods=["GET"])
@login_required
@sys_admin_required()
def search_campaigns():
    org_id = request.args.get("orgId")
    query = request.args.get("query")
    return campaign_api.search_campaigns(org_id, query, g.current_user)
