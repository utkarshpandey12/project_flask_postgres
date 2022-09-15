import datetime

from sqlalchemy.exc import IntegrityError

from ... import db
from ..models.main import Role


def get_roles():
    return Role.query.filter(Role.org_id.is_(None)).all()


def get_role_with_ids(role_ids):
    return Role.query.filter(Role.id.in_(role_ids)).all()


def get_role_with_id(role_id):
    return Role.query.get(role_id)


def get_role_with_name(name):
    return Role.query.filter(
        Role.org_id.is_(None), db.func.lower(Role.name) == name.strip().lower()
    ).first()


def create_role(name, role_type, current_user):
    now = datetime.datetime.now()
    role = Role(
        name=name,
        role_type=role_type,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(role)
    db.session.flush()
    return role


def delete_role(role):
    try:
        db.session.delete(role)
        db.session.flush()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def update_role(role, name, current_user):
    now = datetime.datetime.now()
    role.name = name
    role.updated_at = now
    role.updated_by_user = current_user


def get_org_roles(org_id):
    return Role.query.filter(Role.org_id == org_id).all()
