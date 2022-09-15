from flask import g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import subscription as subscription_api


@main.route("/v1/orgs/<int:org_id>/subscriptions/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_subscription(org_id):
    return subscription_api.create_subscription(org_id, request.json, g.current_user)


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/", methods=["PUT"]
)
@login_required
@sys_admin_required()
@transaction()
def update_subscription(org_id, subscription_id):
    return subscription_api.update_subscription(
        org_id, subscription_id, request.json, g.current_user
    )


@main.route("/v1/orgs/<int:org_id>/subscriptions/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_subscriptions_for_org(org_id):
    return subscription_api.get_all_subscriptions_for_org(org_id)


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_subscriptions_details(org_id, subscription_id):
    return subscription_api.get_subscription_details(org_id, subscription_id)


@main.route(
    "/v1/subscriptions/<int:subscription_id>/invite-transactions/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_invite_transaction(subscription_id):
    return subscription_api.create_invite_transaction(
        subscription_id, request.json, g.current_user
    )


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/modules/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_subscription_modules(org_id, subscription_id):
    return subscription_api.update_subscription_modules(
        org_id, subscription_id, request.json
    )


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/attributes/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_subscription_attributes(org_id, subscription_id):
    return subscription_api.update_subscription_attributes(
        org_id, subscription_id, request.json
    )


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/flow-templates/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_subscription_flow_templates(org_id, subscription_id):
    return subscription_api.update_subscription_flow_templates(
        org_id, subscription_id, request.json
    )


@main.route(
    "/v1/orgs/<int:org_id>/subscriptions/<int:subscription_id>/countries/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_subscription_countries(org_id, subscription_id):
    return subscription_api.update_subscription_countries(
        org_id, subscription_id, request.json
    )


@main.route(
    "/v1/subscriptions/<int:subscription_id>/invite-transactions/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_invite_transactions(subscription_id):
    return subscription_api.get_invite_transactions(subscription_id)


@main.route(
    "/v1/orgs/<int:org_id>/invite-balance/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_invite_balance(org_id):
    return subscription_api.get_invite_balance(org_id)
