from flask import request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import plan as plan_api


@main.route("/v1/plans/<int:plan_id>/modules/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_plan_modules(plan_id):
    return plan_api.update_plan_modules(plan_id, request.json)


@main.route("/v1/plans/<int:plan_id>/attributes/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_plan_attributes(plan_id):
    return plan_api.update_plan_attributes(plan_id, request.json)


@main.route("/v1/plans/<int:plan_id>/flow-templates/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_flow_templates(plan_id):
    return plan_api.update_plan_flow_templates(plan_id, request.json)


@main.route("/v1/plans/<int:plan_id>/countries/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def update_plan_countries(plan_id):
    return plan_api.update_plan_countries(plan_id, request.json)
