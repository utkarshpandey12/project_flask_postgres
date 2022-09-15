import datetime

import shortuuid
from sqlalchemy.orm import contains_eager

from ... import db
from ..models import main as constants
from ..models.main import Org, OrgUser


def get_org_with_uuid(uuid):
    return Org.query.filter(Org.uuid == uuid).first()


def get_org_with_name(name):
    return Org.query.filter(db.func.lower(Org.name) == name.strip().lower()).first()


def get_all_orgs():
    return Org.query.all()


def get_org_with_id(org_id):
    return Org.query.get(org_id)


def create_org(name, display_name, spoken_name, timezone, current_user):
    uuid = shortuuid.uuid()
    now = datetime.datetime.now()
    org = Org(
        name=name,
        display_name=display_name,
        spoken_name=spoken_name,
        uuid=uuid,
        timezone=timezone,
        settings={},
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(org)
    db.session.flush()
    return org


def get_org_user_with_org_and_user(org, user):
    return OrgUser.query.filter(OrgUser.org == org, OrgUser.user == user).first()


def create_org_user(user, is_owner, org, current_user):
    now = datetime.datetime.now()
    org_user = OrgUser(
        user=user,
        is_owner=is_owner,
        status=constants.ORG_USER_STATUS_ACTIVE,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(org_user)
    db.session.flush()
    return org_user


def update_org(name, display_name, spoken_name, timezone, org, current_user):
    now = datetime.datetime.now()
    org.name = name
    org.display_name = display_name
    org.spoken_name = spoken_name
    org.timezone = timezone
    org.updated_at = now
    org.updated_by_user = current_user
    db.session.add(org)
    db.session.flush()
    return org


def get_org_user_with_org(org, is_owner=None):
    query = OrgUser.query.filter(OrgUser.org == org)
    if is_owner is not None:
        query = query.filter(OrgUser.is_owner == is_owner)
    return query.first()


def get_org_user_details_with_org(org):
    return (
        OrgUser.query.join(OrgUser.user)
        .options(contains_eager(OrgUser.user))
        .filter(OrgUser.org == org)
        .all()
    )
