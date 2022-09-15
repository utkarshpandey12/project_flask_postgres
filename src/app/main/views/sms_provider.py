from flask_login import login_required

from ...decorators.permission import sys_admin_required
from .. import main
from ..api import sms_provider as sms_provider_api


@main.route("/v1/sms-providers/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_sms_providers():
    return sms_provider_api.get_all_sms_providers()
