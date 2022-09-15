from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import org as org_dao
from ..dao import role as role_dao
from ..schemas import role as role_schemas


def get_all_roles():
    roles = role_dao.get_roles()
    res = role_schemas.role_schema.dump(roles, many=True)
    return response.success(res)


def get_role(role_id):
    role = role_dao.get_role_with_id(role_id)
    if not role:
        return response.not_found()

    res = role_schemas.role_schema.dump(role)
    return response.success(res)


def create_role(data, current_user):
    try:
        data = role_schemas.create_role_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    role_type = data.get("role_type")

    errors = {}

    existing_role = role_dao.get_role_with_name(name)
    if existing_role:
        errors["name"] = ["A role with this name already exists."]

    if errors:
        return response.validation_failed(errors)

    role = role_dao.create_role(name, role_type, current_user)
    res = role_schemas.create_role_schema.dump(role)

    return response.success(res)


def delete_role(role_id, current_user):
    role = role_dao.get_role_with_id(role_id)

    if not role:
        return response.not_found()

    errors = {}

    is_deleted = role_dao.delete_role(role)

    if not is_deleted:
        errors["message"] = [f"{role.name} cannot be deleted as it is currently in use"]

    if errors:
        return response.validation_failed(errors)

    return response.success({})


def update_role(role_id, data, current_user):
    role = role_dao.get_role_with_id(role_id)
    if not role:
        return response.not_found()

    try:
        data = role_schemas.update_role_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")

    errors = {}

    existing_role = role_dao.get_role_with_name(name)

    if existing_role and existing_role.id != role.id:
        errors["name"] = ["A role with this name already exists."]

    if errors:
        return response.validation_failed(errors)

    role_dao.update_role(role, name, current_user)
    res = role_schemas.update_role_schema.dump(role)

    return response.success(res)


def get_org_roles(org_id):
    org = org_dao.get_org_with_id(org_id)
    if not org:
        return response.not_found()

    roles = role_dao.get_org_roles(org_id)
    res = role_schemas.role_schema.dump(roles, many=True)
    return response.success(res)
