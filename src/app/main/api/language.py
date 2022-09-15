from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import language as language_dao
from ..schemas import language as language_schemas


def get_all_languages():
    languages = language_dao.get_all_language()
    res = language_schemas.language_schema.dump(languages, many=True)
    return response.success(res)


def get_language(language_id):
    language = language_dao.get_language_by_id(language_id)
    if not language:
        return response.not_found()
    res = language_schemas.language_schema.dump(language)
    return response.success(res)


def create_language(data, current_user):
    try:
        data = language_schemas.create_language_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    identifier = data.get("identifier")

    errors = {}

    language_with_same_name = language_dao.get_language_by_name(name)

    if language_with_same_name:
        errors["name"] = ["A language with this name already exists"]

    language_with_same_identifier = language_dao.get_language_by_identifier(identifier)

    if language_with_same_identifier:
        errors["identifier"] = ["A language with this identifier already exists"]

    if errors:
        return response.validation_failed(errors)

    language = language_dao.create_language(name, identifier)

    res = language_schemas.language_schema.dump(language)
    return response.success(res)


def update_language(language_id, data, current_user):
    language = language_dao.get_language_by_id(language_id)
    if not language:
        return response.not_found()

    try:
        data = language_schemas.update_language_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    identifier = data.get("identifier")

    errors = {}

    language_with_same_name = language_dao.get_language_by_name(name)

    language_with_same_identifier = language_dao.get_language_by_identifier(identifier)

    if language_with_same_name and language_with_same_name.id != language_id:
        errors["name"] = ["A Language with this name already exists"]

    if (
        language_with_same_identifier
        and language_with_same_identifier.id != language_id
    ):
        errors["identifier"] = ["A Language with this identifier already exists"]

    if errors:
        return response.validation_failed(errors)

    language = language_dao.update_language(language, name, identifier, current_user)

    res = language_schemas.language_schema.dump(language)
    return response.success(res)


def delete_language(language_id, current_user):
    language = language_dao.get_language_by_id(language_id)

    if not language:
        return response.not_found()

    errors = {}

    is_deleted = language_dao.delete_language(language)

    if not is_deleted:
        errors["message"] = [
            f"{language.name} cannot be deleted as it is currently in use"
        ]

    if errors:
        return response.validation_failed(errors)

    return response.success({})
