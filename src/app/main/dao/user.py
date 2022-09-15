import datetime

from sqlalchemy import exists

from ... import db
from ..models import main as constants
from ..models.main import (
    Module,
    OrgUser,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)


def get_user_permissions(user):
    return (
        Permission.query.join(Module, Permission.module_id == Module.id)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .join(UserRole, RolePermission.role_id == UserRole.role_id)
        .options(db.contains_eager(Permission.module))
        .filter(UserRole.user == user, UserRole.org_id.is_(None))
        .all()
    )


def get_user_permission_identifiers(user):
    permissions = get_user_permissions(user)
    return {p.fully_qualified_identifier for p in permissions}


def get_user_with_id(user_id):
    return User.query.get(user_id)


def get_user_with_email(email):
    return User.query.filter(db.func.lower(User.email) == email.strip().lower()).first()


def get_user_with_mobile(mobile):
    return User.query.filter(User.mobile == mobile).first()


def create_user(
    name,
    email,
    password,
    mobile,
    must_change_password,
    is_email_verified,
    is_sys_admin,
    current_user,
):
    now = datetime.datetime.now()
    user = User(
        name=name,
        email=email,
        mobile=mobile,
        must_change_password=must_change_password,
        is_email_verified=is_email_verified,
        is_sys_admin=is_sys_admin,
        created_at=now,
        created_by_user=[current_user],
        updated_at=now,
        updated_by_user=[current_user],
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def create_user_role(user, role, org, current_user):
    now = datetime.datetime.now()
    user_role = UserRole(
        user=user,
        role=role,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(user_role)
    db.session.flush()
    return user_role


def create_role(name, role_type, org, current_user):
    now = datetime.datetime.now()

    role = Role(
        name=name,
        role_type=role_type,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )

    db.session.add(role)
    db.session.flush()
    return role


def update_user(
    user,
    name,
    email,
    mobile,
    current_user,
):
    user.name = name
    user.email = email
    user.mobile = mobile
    user.updated_at = datetime.datetime.now()
    user.updated_by_user = current_user


def delete_user_roles_with_user_id(user):
    return UserRole.query.filter(UserRole.user == user).delete()


def get_roles_with_user_id(user):
    return (
        Role.query.join(UserRole, Role.id == UserRole.role_id)
        .filter(UserRole.user == user)
        .all()
    )


def get_users():
    return User.query.filter(~exists().where(OrgUser.user_id == User.id)).all()


def get_transcriber_users():
    return User.query.filter(
        UserRole.query.join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == User.id,
            Role.role_type == constants.ROLE_TYPE_TRANSCRIBER,
        )
        .exists()
    ).all()


def user_has_role_type(user_id, role_type):
    user = (
        db.session.query(UserRole.id)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.role_type == role_type,
        )
        .first()
    )
    return user is not None
