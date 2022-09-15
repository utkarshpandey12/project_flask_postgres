from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import telephony_provider as telephony_provider_api


@main.route("/v1/telephony-providers/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_telephony_providers():
    return telephony_provider_api.get_all_telephony_providers()
