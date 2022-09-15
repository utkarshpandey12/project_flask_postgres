from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import language as language_dao
from ..dao import org as org_dao
from ..dao import transcriber_team as transcriber_team_dao
from ..dao import user as user_dao
from ..models import main as constants
from ..schemas import transcriber_team as transcriber_team_schemas


def create_transcriber_team(data, current_user):
    try:
        data = transcriber_team_schemas.create_transcriber_team_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    language_id = data.get("language").get("id")
    is_default = data.get("is_default")

    language = language_dao.get_language_by_id(language_id)

    errors = {}

    if not language:
        errors["language"] = {"id": ["Invalid language id."]}

    if errors:
        return response.validation_failed(errors)

    transcriber_team_with_same_name = transcriber_team_dao.get_transcriber_team_by_name(
        name
    )

    if transcriber_team_with_same_name:
        errors["name"] = ["A transcriber team with this name already exists"]

    if errors:
        return response.validation_failed(errors)

    existing_transcriber_team = (
        transcriber_team_dao.get_default_transcriber_team_by_language_id(language_id)
    )

    if not existing_transcriber_team:
        # If this is the first transcriber team for this language, mark it as default.
        is_default = True
    elif is_default:
        # If the new team is marked as default, mark the existing default
        # team as not default.
        transcriber_team_dao.update_transcriber_teams_by_language_id(
            language_id, is_default=False
        )

    transcriber_team = transcriber_team_dao.create_transcriber_team(
        name, language, is_default, current_user
    )
    res = transcriber_team_schemas.transcriber_team_schema.dump(transcriber_team)
    return response.success(res)


def update_transcriber_team(transcriber_team_id, data, current_user):
    transcriber_team = transcriber_team_dao.get_transcriber_team_with_id(
        transcriber_team_id
    )
    if not transcriber_team:
        return response.not_found()

    try:
        data = transcriber_team_schemas.update_transcriber_team_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    is_default = data.get("is_default")

    errors = {}

    transcriber_team_with_same_name = transcriber_team_dao.get_transcriber_team_by_name(
        name
    )

    if (
        transcriber_team_with_same_name
        and transcriber_team_with_same_name.id != transcriber_team_id
    ):
        errors["name"] = ["A transcriber team with this name already exists"]

    if transcriber_team.is_default and not is_default:
        errors["isDefault"] = ["A default transcriber team cannot be made non-default"]

    if errors:
        return response.validation_failed(errors)

    if not transcriber_team.is_default and is_default:
        # If the team is marked as default, mark the existing default
        # team as not default.
        transcriber_team_dao.update_transcriber_teams_by_language_id(
            transcriber_team.language_id, is_default=False
        )

    transcriber_team = transcriber_team_dao.update_transcriber_team(
        transcriber_team, name, is_default, current_user
    )
    res = transcriber_team_schemas.transcriber_team_schema.dump(transcriber_team)
    return response.success(res)


def add_transcriber(transcriber_team_id, data, current_user):
    transcriber_team = transcriber_team_dao.get_transcriber_team_with_id(
        transcriber_team_id
    )
    if not transcriber_team:
        return response.not_found()

    try:
        data = transcriber_team_schemas.add_transcriber_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    user_id = data.get("transcriber_user", {}).get("id")
    user = user_dao.get_user_with_id(user_id)

    errors = {}

    if not user:
        errors["user"] = {"id": ["Invalid user id"]}

    if errors:
        return response.validation_failed(errors)

    is_transcriber = user_dao.user_has_role_type(
        user_id, constants.ROLE_TYPE_TRANSCRIBER
    )

    if not is_transcriber:
        errors["user"] = {"id": ["Cannot add non-transcriber user to transcriber team"]}

    if errors:
        return response.validation_failed(errors)

    transcriber_team_user = transcriber_team_dao.get_transcriber_team_user(
        transcriber_team.id, user.id
    )

    if transcriber_team_user:
        errors["user"] = {
            "id": [f"This transcriber is already a member of {transcriber_team.name}"]
        }

    if errors:
        return response.validation_failed(errors)

    transcriber_team_dao.add_transcriber_team_user(transcriber_team, user)
    return response.success({})


def delete_transcriber(transcriber_team_id, user_id, current_user):
    transcriber_team_user = transcriber_team_dao.get_transcriber_team_user(
        transcriber_team_id, user_id
    )

    if not transcriber_team_user:
        return response.not_found()

    transcriber_team_dao.delete_transcriber_team_user(transcriber_team_user)
    return response.success({})


def get_transcriber_teams():
    transcriber_teams = transcriber_team_dao.get_all_transcriber_teams()
    res = transcriber_team_schemas.transcriber_team_schema.dump(
        transcriber_teams, many=True
    )
    return response.success(res)


def get_transcriber_team(transcriber_team_id):
    transcriber_team = transcriber_team_dao.get_transcriber_team_with_id(
        transcriber_team_id
    )
    if not transcriber_team:
        return response.not_found()

    res = transcriber_team_schemas.transcriber_team_details_schema.dump(
        transcriber_team
    )
    return response.success(res)


def get_transcriber_team_orgs():
    transcriber_team_orgs = transcriber_team_dao.get_all_transcriber_team_orgs()
    res = transcriber_team_schemas.transcriber_team_org_schema.dump(
        transcriber_team_orgs, many=True
    )
    return response.success(res)


def add_transcriber_team_org(data, current_user):
    try:
        data = transcriber_team_schemas.add_transcriber_team_org_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    transcriber_team_id = data.get("transcriber_team_id")
    org_id = data.get("org_id")

    errors = {}

    transcriber_team = transcriber_team_dao.get_transcriber_team_with_id(
        transcriber_team_id
    )
    if not transcriber_team:
        errors["transcriberTeamId"] = ["Invalid transcriber team id"]

    org = org_dao.get_org_with_id(org_id)
    if not org:
        errors["orgId"] = ["Invalid org id"]

    if errors:
        return response.validation_failed(errors)

    transcriber_team_org = (
        transcriber_team_dao.get_transcriber_team_org_with_team_id_and_org_id(
            transcriber_team_id, org_id
        )
    )
    if transcriber_team_org:
        errors["message"] = f"{transcriber_team.name} is already assigned to {org.name}"

    if errors:
        return response.validation_failed(errors)

    transcriber_team_org = (
        transcriber_team_dao.get_transcriber_team_org_with_org_id_and_language_id(
            org_id, transcriber_team.language_id
        )
    )
    if transcriber_team_org:
        errors["message"] = (
            f"Another team ({transcriber_team_org.transcriber_team.name}) "
            f"is already assigned to {org.name} for {transcriber_team.language.name}"
        )

    if errors:
        return response.validation_failed(errors)

    transcriber_team_org = transcriber_team_dao.add_transcriber_team_org(
        transcriber_team, org
    )
    res = transcriber_team_schemas.transcriber_team_org_schema.dump(
        transcriber_team_org
    )
    return response.success(res)


def delete_transcriber_team_org(transcriber_team_org_id, current_user):
    transcriber_team_org = transcriber_team_dao.get_transcriber_team_org_with_id(
        transcriber_team_org_id
    )
    if not transcriber_team_org:
        return response.not_found()

    transcriber_team_dao.delete_transcriber_team_org(transcriber_team_org)
    return response.success({})
