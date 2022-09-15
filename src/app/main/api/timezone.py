from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import timezone as timezone_dao
from ..schemas import timezone as timezone_schemas


def get_all_timezones():
    timezone = timezone_dao.get_all_timezones()
    res = timezone_schemas.timezone_schema.dump(timezone, many=True)
    return response.success(res)


def create_timezone(data):
    try:
        data = timezone_schemas.create_timezone_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    identifier = data.get("identifier")
    other_identifiers = data.get("other_identifiers")

    errors = {}

    existing_timezone_with_name = timezone_dao.get_timezone_with_name(name)
    if existing_timezone_with_name:
        errors["name"] = ["A timezone with this name already exists."]
    existing_timezone_with_identifier = timezone_dao.get_timezone_with_identifier(
        identifier
    )
    if existing_timezone_with_identifier:
        errors["identifier"] = ["A timezone with this identifier already exists."]
    existing_other_identifiers = []
    for other_identifier in other_identifiers:
        existing_timezone_with_other_identifier = (
            timezone_dao.get_timezone_with_identifier(other_identifier)
        )
        if existing_timezone_with_other_identifier:
            existing_other_identifiers.append(other_identifier)
    if existing_other_identifiers:
        errors["otherIdentifiers"] = [
            f"A timezone with the following identifiers "
            f"already exists: {','.join(existing_other_identifiers)}"
        ]
    if errors:
        return response.validation_failed(errors)

    timezone = timezone_dao.create_timezone(name, identifier, other_identifiers)
    res = timezone_schemas.timezone_schema.dump(timezone)
    return response.success(res)
