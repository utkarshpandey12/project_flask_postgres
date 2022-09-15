from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import country as country_dao
from ..dao import org as org_dao
from ..dao import sender_id as sender_id_dao
from ..dao import sms_provider as sms_provider_dao
from ..schemas import sender_id as sender_id_schemas


def create_sender_id(org_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    try:
        data = sender_id_schemas.create_sender_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    country_id = data.get("country_id")
    sms_provider_id = data.get("sms_provider_id")
    value = data.get("value")

    errors = {}

    country = country_dao.get_country_with_id(country_id)
    sms_provider = sms_provider_dao.get_sms_provider_with_id(sms_provider_id)
    existing_sender_id_with_value = sender_id_dao.get_sender_id_with_value(value)

    existing_sender_id_with_criteria = None
    if country and sms_provider:
        existing_sender_id_with_criteria = sender_id_dao.get_sender_id_with_criteria(
            org, country, sms_provider
        )

    if not country:
        errors["countryId"] = ["A country with this id does not exist."]

    if not sms_provider:
        errors["smsProviderId"] = ["A sms provider with this id does not exist."]

    if existing_sender_id_with_value:
        errors["value"] = ["This sender id is already assigned."]

    if existing_sender_id_with_criteria:
        errors["message"] = (
            "A sender id already exists for the specified organization, "
            "country and SMS provider."
        )

    if errors:
        return response.validation_failed(errors)

    sender_id = sender_id_dao.create_sender_id(
        country,
        sms_provider,
        value,
        org,
        current_user,
    )
    res = sender_id_schemas.sender_id_schema.dump(sender_id)
    return response.success(res)


def update_sender_id(org_id, sender_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    sender_id_obj = sender_id_dao.get_sender_id_with_id_and_org(sender_id, org)

    if not sender_id_obj:
        return response.not_found()

    try:
        data = sender_id_schemas.update_sender_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    value = data.get("value")

    existing_sender_id_with_value = sender_id_dao.get_sender_id_with_value(value)

    errors = {}

    if (
        existing_sender_id_with_value
        and sender_id_obj
        and sender_id_obj.id != existing_sender_id_with_value.id
    ):
        errors["value"] = ["This sender id is already assigned."]

    if errors:
        return response.validation_failed(errors)

    sender_id = sender_id_dao.update_sender_id(sender_id_obj, value, current_user)
    res = sender_id_schemas.sender_id_schema.dump(sender_id)
    return response.success(res)


def delete_sender_id(org_id, sender_id, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    sender_id_obj = sender_id_dao.get_sender_id_with_id_and_org(sender_id, org)

    if not sender_id_obj:
        return response.not_found()
    sender_id_dao.delete_sender_id(sender_id_obj)
    return response.success({})


def get_all_sender_ids(org_id):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    sender_id = sender_id_dao.get_all_sender_ids_with_org(org)
    res = sender_id_schemas.sender_id_schema.dump(sender_id, many=True)
    return response.success(res)


def get_sender_id(org_id, sender_id):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    sender_id = sender_id_dao.get_sender_id_with_id_and_org(sender_id, org)
    res = sender_id_schemas.sender_id_schema.dump(sender_id)
    return response.success(res)
