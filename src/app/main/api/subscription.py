from datetime import datetime

from marshmallow.exceptions import ValidationError

from ...utils import response
from ..api import plan as plan_api
from ..dao import org as org_dao
from ..dao import plan as plan_dao
from ..dao import subscription as subscription_dao
from ..models import main as constants
from ..schemas import subscription as subscription_schemas


def validate_subscription(org, data, subscription_id=None):
    try:
        data = subscription_schemas.create_update_subscription_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    start_on = data.get("start_on")
    end_on = data.get("end_on")
    renewal_grace_period_days = data.get("renewal_grace_period_days")

    errors = {}

    if start_on >= end_on:
        errors["endOn"] = ["End date must be later than start date"]

    today = datetime.now().date()
    if end_on < today:
        errors["endOn"] = ["End date must not be in the past"]

    if errors:
        return None, errors

    subscription_check = subscription_dao.get_subscription_with_org_id_and_dates(
        org.id, start_on, end_on, subscription_id
    )

    if subscription_check:
        errors[
            "message"
        ] = "Subscription dates must not overlap with an existing subscription"

    if errors:
        return None, errors

    return (start_on, end_on, renewal_grace_period_days), errors


def create_subscription(org_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    valid_data, errors = validate_subscription(org, data)

    if errors:
        return response.validation_failed(errors)

    start_on, end_on, renewal_grace_period_days = valid_data

    name = "{} - {}".format(org.name, "Plan")

    plan = plan_dao.create_plan(name, start_on, end_on, org, current_user)
    subscription = subscription_dao.create_subscription(
        plan, start_on, end_on, renewal_grace_period_days, org, current_user
    )
    res = subscription_schemas.subscription_schema.dump(subscription)
    return response.success(res)


def update_subscription(org_id, subscription_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    valid_data, errors = validate_subscription(org, data, subscription_id)

    if errors:
        return response.validation_failed(errors)

    start_on, end_on, renewal_grace_period_days = valid_data

    plan_dao.update_plan(subscription.plan, start_on, end_on, current_user)
    subscription = subscription_dao.update_subscription(
        subscription, start_on, end_on, renewal_grace_period_days, current_user
    )
    res = subscription_schemas.subscription_schema.dump(subscription)
    return response.success(res)


def get_all_subscriptions_for_org(org_id):
    subscriptions = subscription_dao.get_subscriptions_with_org_id(org_id)
    res = subscription_schemas.subscription_schema.dump(subscriptions, many=True)
    return response.success(res)


def get_subscription_details(org_id, subscription_id):

    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    res = subscription_schemas.subscription_details_schema.dump(subscription)
    return response.success(res)


def create_invite_transaction(subscription_id, data, current_user):
    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    try:
        data = subscription_schemas.create_invite_transaction_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    errors = {}

    txn_type = data.get("txn_type")
    amount = data.get("amount")
    today = datetime.now().date()

    if subscription.end_on < today:
        errors["txn_type"] = ["Cannot add transaction for an expired subscription"]

    if (
        txn_type
        in [
            constants.INVITE_TRANSACTION_TYPE_SUBSCRIPTION,
            constants.INVITE_TRANSACTION_TYPE_TOP_UP,
        ]
        and amount <= 0
    ):
        errors["amount"] = ["Amount must be greater than zero"]

    if txn_type == constants.INVITE_TRANSACTION_TYPE_ADJUSTMENT and amount == 0:
        errors["amount"] = ["Amount must not be zero"]

    if errors:
        return response.validation_failed(errors)

    org = subscription.org
    org_owner = org_dao.get_org_user_with_org(org, is_owner=True)
    owner = org_owner.user

    invite_transaction = subscription_dao.create_invite_transaction(
        subscription, txn_type, amount, org, current_user
    )
    subscription_dao.create_user_invite_transaction(
        subscription, owner, txn_type, amount, org, current_user
    )

    user_invite_balance = subscription_dao.calculate_user_invite_balance(
        owner, org, subscription
    )
    user_invite_balance_obj = subscription_dao.get_user_invite_balance(owner, org)
    subscription_dao.update_user_invite_balance(
        user_invite_balance_obj, user_invite_balance
    )

    org_invite_balance = subscription_dao.calculate_org_invite_balance(
        org, subscription
    )
    org_invite_balance_obj = subscription_dao.get_org_invite_balance(org)
    subscription_dao.update_org_invite_balance(
        org_invite_balance_obj, org_invite_balance
    )

    res = subscription_schemas.invite_transaction_schema.dump(invite_transaction)
    return response.success(res)


def update_subscription_modules(org_id, subscription_id, data):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    return plan_api.update_plan_modules(subscription.plan_id, data)


def update_subscription_attributes(org_id, subscription_id, data):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    return plan_api.update_plan_attributes(subscription.plan_id, data)


def update_subscription_flow_templates(org_id, subscription_id, data):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    return plan_api.update_plan_flow_templates(subscription.plan_id, data)


def update_subscription_countries(org_id, subscription_id, data):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    return plan_api.update_plan_countries(subscription.plan_id, data)


def get_invite_transactions(subscription_id):
    subscription = subscription_dao.get_subscription_with_id(subscription_id)

    if not subscription:
        return response.not_found()

    inv_transactions = subscription_dao.get_invite_transactions_with_subscription_id(
        subscription_id
    )

    res = subscription_schemas.invite_transaction_schema.dump(
        inv_transactions,
        many=True,
    )
    return response.success(res)


def get_invite_balance(org_id):
    org = org_dao.get_org_with_id(org_id)
    if not org:
        return response.not_found()
    inv_balance = subscription_dao.get_invite_balance(org_id)
    res = subscription_schemas.invite_balance_schema.dump(inv_balance)
    return response.success(res)
