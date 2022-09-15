from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import country as country_dao
from ..schemas import country as country_schemas


def get_all_countries():
    countries = country_dao.get_all_countries()
    res = country_schemas.country_schema.dump(countries, many=True)
    return response.success(res)


def get_country(country_id):
    country = country_dao.get_country_with_id(country_id)
    if not country:
        return response.not_found()

    res = country_schemas.country_schema.dump(country)
    return response.success(res)


def create_country(data):
    try:
        data = country_schemas.create_country_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    country_code = data.get("country_code")

    errors = {}

    country_with_same_name = country_dao.get_country_by_name(name)

    if country_with_same_name:
        errors["name"] = ["A country with this name already exists"]

    if errors:
        return response.validation_failed(errors)

    country = country_dao.create_country(name, country_code)
    res = country_schemas.country_schema.dump(country)

    return response.success(res)


def delete_country(country_id, current_user):
    country = country_dao.get_country_with_id(country_id)

    if not country:
        return response.not_found()

    errors = {}

    is_deleted = country_dao.delete_country(country)

    if not is_deleted:
        errors["message"] = [
            f"{country.name} cannot be deleted as it is currently in use"
        ]

    if errors:
        return response.validation_failed(errors)

    return response.success({})


def update_country(country_id, data, current_user):
    country = country_dao.get_country_with_id(country_id)
    if not country:
        return response.not_found()

    try:
        data = country_schemas.update_country_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    country_code = data.get("country_code")

    errors = {}

    country_with_same_name = country_dao.get_country_by_name(name)

    country_with_same_country_code = country_dao.get_country_by_country_code(
        country_code
    )

    if country_with_same_name and country_with_same_name.id != country_id:
        errors["name"] = ["A Country with this name already exists"]

    if (
        country_with_same_country_code
        and country_with_same_country_code.id != country_id
    ):
        errors["code"] = ["A Country with this code already exists"]

    if errors:
        return response.validation_failed(errors)

    country = country_dao.update_country(country, name, country_code, current_user)

    res = country_schemas.country_schema.dump(country)
    return response.success(res)
