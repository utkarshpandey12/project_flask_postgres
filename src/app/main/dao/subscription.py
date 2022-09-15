import datetime

from ... import db
from ..models.main import (
    InviteBalance,
    InviteTransaction,
    Subscription,
    UserInviteBalance,
    UserInviteTransaction,
)


def create_subscription(
    plan, start_on, end_on, renewal_grace_period_days, org, current_user
):
    now = datetime.datetime.now()
    subscription = Subscription(
        plan=plan,
        start_on=start_on,
        end_on=end_on,
        renewal_grace_period_days=renewal_grace_period_days,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(subscription)
    db.session.flush()
    return subscription


def update_subscription(
    subscription, start_on, end_on, renewal_grace_period_days, current_user
):
    now = datetime.datetime.now()
    subscription.start_on = start_on
    subscription.end_on = end_on
    subscription.renewal_grace_period_days = renewal_grace_period_days
    subscription.updated_at = now
    subscription.updated_by_user = current_user
    db.session.add(subscription)
    db.session.flush()
    return subscription


def get_subscription_with_org_id_and_dates(
    org_id, start_on, end_on, excluded_subscription_id=None
):
    query = Subscription.query.filter(
        Subscription.org_id == org_id,
        Subscription.start_on <= end_on,
        Subscription.end_on >= start_on,
    )
    if excluded_subscription_id:
        query = query.filter(Subscription.id != excluded_subscription_id)
    return query.first()


def get_subscriptions_with_org_id(org_id):
    return Subscription.query.filter(Subscription.org_id == org_id).all()


def get_subscription_with_id(subscription_id):
    return Subscription.query.get(subscription_id)


def create_invite_transaction(subscription, txn_type, amount, org, current_user):
    now = datetime.datetime.now()
    invite_transaction = InviteTransaction(
        subscription=subscription,
        txn_on=now.date(),
        txn_type=txn_type,
        amount=amount,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(invite_transaction)
    db.session.flush()
    return invite_transaction


def create_user_invite_transaction(
    subscription, user, txn_type, amount, org, current_user
):
    now = datetime.datetime.now()

    user_invite_transaction = UserInviteTransaction(
        subscription=subscription,
        user=user,
        counterparty_user=None,
        txn_on=now.date(),
        txn_type=txn_type,
        amount=amount,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(user_invite_transaction)
    db.session.flush()
    return user_invite_transaction


def calculate_user_invite_balance(user, org, subscription):
    result = (
        db.session.query(
            db.func.sum(UserInviteTransaction.amount),
        )
        .filter(
            UserInviteTransaction.org == org,
            UserInviteTransaction.subscription == subscription,
            UserInviteTransaction.user == user,
        )
        .first()
    )
    return result[0]


def create_user_invite_balance(org, owner, amount):
    user_invite_balance = UserInviteBalance(org=org, user=owner, amount=amount)
    db.session.add(user_invite_balance)
    db.session.flush()
    return user_invite_balance


def update_user_invite_balance(user_invite_balance, amount):
    user_invite_balance.amount = amount


def get_user_invite_balance(user, org):
    return UserInviteBalance.query.filter(
        UserInviteBalance.org == org,
        UserInviteBalance.user == user,
    ).first()


def calculate_org_invite_balance(org, subscription):
    result = (
        db.session.query(
            db.func.sum(InviteTransaction.amount),
        )
        .filter(
            InviteTransaction.org == org, InviteTransaction.subscription == subscription
        )
        .first()
    )
    return result[0]


def create_org_invite_balance(org, amount):
    org_invite_balance = InviteBalance(org=org, amount=amount)
    db.session.add(org_invite_balance)
    db.session.flush()
    return org_invite_balance


def update_org_invite_balance(org_invite_balance, amount):
    org_invite_balance.amount = amount


def get_org_invite_balance(org):
    return InviteBalance.query.filter(InviteBalance.org == org).first()


def get_invite_transactions_with_subscription_id(subscription_id):
    return InviteTransaction.query.filter(
        InviteTransaction.subscription_id == subscription_id
    ).all()


def get_invite_balance(org_id):
    return InviteBalance.query.filter(InviteBalance.org_id == org_id).first()
