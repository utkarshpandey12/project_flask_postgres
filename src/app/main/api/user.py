from marshmallow.exceptions import ValidationError

from ...utils import crypto, phone_number, response
from ..dao import role as role_dao
from ..dao import user as user_dao
from ..models import main as constants
from ..schemas import user as user_schemas


def validate_user(user, data):
    try:
        data = user_schemas.create_update_user_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    email = data.get("email")
    country_code = data.get("country_code")
    mobile_no = data.get("mobile_no")
    mobile = phone_number.format_e164(country_code, mobile_no)
    role_data = data.get("roles")

    user_email_check = user_dao.get_user_with_email(email)
    user_mobile_no_check = user_dao.get_user_with_mobile(mobile)

    errors = {}

    if user_email_check is not None and (
        user is None or user_email_check.id != user.id
    ):
        errors["email"] = ["A user with this email address already exists."]

    if user_mobile_no_check is not None and (
        user is None or user_mobile_no_check.id != user.id
    ):
        errors["mobile_no"] = ["A user with this mobile number already exists."]

    role_ids = []
    for index, role in enumerate(role_data):
        if role["id"] in role_ids:
            role_errors = errors.setdefault("roles", {})
            role_errors[str(index)] = {"id": [f"Duplicate role id - {role['id']}"]}
        role_ids.append(role["id"])

    if errors:
        return None, errors

    roles = role_dao.get_role_with_ids(role_ids)
    valid_role_ids = [role.id for role in roles]
    for index, role in enumerate(role_data):
        if role["id"] not in valid_role_ids:
            role_errors = errors.setdefault("roles", {})
            role_errors[str(index)] = {"id": [f"Invalid role id - {role['id']}"]}

    if errors:
        return None, errors

    role_dict = {role.id: role for role in roles}
    for index, role in enumerate(role_data):
        role_obj = role_dict[role["id"]]
        if (
            role_obj.org_id is not None
            or role_obj.role_type == constants.ROLE_TYPE_CUSTOMER
        ):
            role_errors = errors.setdefault("roles", {})
            role_errors[str(index)] = {
                "id": [f"Inapplicable role id for non-org user - {role_obj.id}"]
            }

    if errors:
        return None, errors

    return (name, email, mobile, roles), errors


def create_user(data, current_user):
    valid_data, errors = validate_user(None, data)

    if errors:
        return response.validation_failed(errors)

    name, email, mobile, roles = valid_data

    password = crypto.generate_random_string(length=6)
    user = user_dao.create_user(
        name,
        email,
        password,
        mobile,
        must_change_password=True,
        is_email_verified=True,
        is_sys_admin=False,
        current_user=current_user,
    )

    for role in roles:
        user_dao.create_user_role(user, role, None, current_user)

    user.roles = roles

    res = user_schemas.user_schema.dump(user)
    return response.success(res)


def update_user(user_id, data, current_user):
    user = user_dao.get_user_with_id(user_id)
    if not user:
        return response.not_found()

    valid_data, errors = validate_user(user, data)

    if errors:
        return response.validation_failed(errors)

    name, email, mobile, roles = valid_data

    user_dao.update_user(
        user,
        name,
        email,
        mobile,
        current_user=current_user,
    )

    user_dao.delete_user_roles_with_user_id(user)

    for role in roles:
        user_dao.create_user_role(user, role, None, current_user)

    user.roles = roles

    res = user_schemas.user_schema.dump(user)
    return response.success(res)


def get_user(user_id):
    user = user_dao.get_user_with_id(user_id)

    if not user:
        return response.not_found()

    roles = user_dao.get_roles_with_user_id(user)

    user.roles = roles

    res = user_schemas.user_schema.dump(user)
    return response.success(res)


def get_users():
    users = user_dao.get_users()
    res = user_schemas.user_schema.dump(users, many=True)
    return response.success(res)


def get_transcriber_users():
    users = user_dao.get_transcriber_users()
    res = user_schemas.user_schema.dump(users, many=True)
    return response.success(res)
