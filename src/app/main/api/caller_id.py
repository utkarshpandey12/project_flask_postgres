from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import caller_id as caller_id_dao
from ..dao import country as country_dao
from ..dao import org as org_dao
from ..dao import telephony_provider as telephony_provider_dao
from ..dao import user as user_dao
from ..models import main as constants
from ..schemas import caller_id as caller_id_schemas


################################################################################
# Caller Ids
################################################################################
def create_caller_id(data, current_user):
    try:
        data = caller_id_schemas.create_caller_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    country_id = data.get("country").get("id")
    telephony_provider_id = data.get("telephony_provider").get("id")
    phone_no = data.get("phone_no")

    errors = {}

    country = country_dao.get_country_with_id(country_id)
    if not country:
        errors["country"] = {"id": ["A country with this id does not exist."]}

    telephony_provider = telephony_provider_dao.get_telephony_provider_with_id(
        telephony_provider_id
    )
    if not telephony_provider:
        errors["telephonyProvider"] = {
            "id": ["A telephony provider with this id does not exist."]
        }

    caller_id_with_same_phone_no = caller_id_dao.get_caller_id_with_phone_no(
        phone_no, for_org=False
    )
    if caller_id_with_same_phone_no:
        errors["phoneNo"] = ["This caller id is already assigned."]

    if errors:
        return response.validation_failed(errors)

    caller_id = caller_id_dao.create_caller_id(
        country=country,
        telephony_provider=telephony_provider,
        phone_no=phone_no,
        current_user=current_user,
    )
    caller_id_dao.create_caller_id_history(
        country=country,
        telephony_provider=telephony_provider,
        phone_no=phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_INSERT,
        current_user=current_user,
    )

    res = caller_id_schemas.caller_id_schema.dump(caller_id)
    return response.success(res)


def update_caller_id(caller_id, data, current_user):
    caller_id_obj = caller_id_dao.get_caller_id_with_id(caller_id, org=None)

    if not caller_id_obj:
        return response.not_found()

    try:
        data = caller_id_schemas.update_caller_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    phone_no = data.get("phone_no")

    errors = {}

    caller_id_obj_with_same_phone_no = caller_id_dao.get_caller_id_with_phone_no(
        phone_no, for_org=False
    )

    if (
        caller_id_obj_with_same_phone_no
        and caller_id_obj
        and caller_id_obj.id != caller_id_obj_with_same_phone_no.id
    ):
        errors["phoneNo"] = ["This caller id is already assigned."]

    if errors:
        return response.validation_failed(errors)

    caller_id = caller_id_dao.update_caller_id(caller_id_obj, phone_no, current_user)

    caller_id_dao.create_caller_id_history(
        country=caller_id_obj.country,
        telephony_provider=caller_id_obj.telephony_provider,
        phone_no=phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_UPDATE,
        current_user=current_user,
    )

    res = caller_id_schemas.caller_id_schema.dump(caller_id)
    return response.success(res)


def delete_caller_id(caller_id, current_user):
    caller_id_obj = caller_id_dao.get_caller_id_with_id(caller_id, org=None)

    if not caller_id_obj:
        return response.not_found()

    caller_id_dao.create_caller_id_history(
        country=caller_id_obj.country,
        telephony_provider=caller_id_obj.telephony_provider,
        phone_no=caller_id_obj.phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_DELETE,
        current_user=current_user,
    )
    caller_id_dao.delete_caller_id(caller_id_obj)
    return response.success({})


def get_caller_ids():
    caller_id = caller_id_dao.get_caller_ids(org=None)
    res = caller_id_schemas.caller_id_schema.dump(caller_id, many=True)
    return response.success(res)


def get_caller_id(caller_id):
    caller_id = caller_id_dao.get_caller_id_with_id(caller_id, org=None)
    res = caller_id_schemas.caller_id_schema.dump(caller_id)
    return response.success(res)


################################################################################
# Org Caller Ids
################################################################################
def create_org_caller_id(org_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    try:
        data = caller_id_schemas.create_org_caller_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    country_id = data.get("country").get("id")
    telephony_provider_id = data.get("telephony_provider").get("id")
    call_type = data.get("call_type")
    user_id = data.get("user").get("id")
    phone_no = data.get("phone_no")

    country = country_dao.get_country_with_id(country_id)
    telephony_provider = telephony_provider_dao.get_telephony_provider_with_id(
        telephony_provider_id
    )
    user = None
    if user_id:
        user = user_dao.get_user_with_id(user_id)
    phone_no_check = caller_id_dao.get_caller_id_with_phone_no(phone_no, for_org=True)

    org_user = None

    if user:
        org_user = org_dao.get_org_user_with_org_and_user(org, user)
    errors = {}

    if not country:
        errors["country"] = {"id": ["A country with this id does not exist."]}

    if not telephony_provider:
        errors["telephonyProvider"] = {
            "id": ["A telephony provider with this id does not exist."]
        }

    if user_id and not user:
        errors["user"] = {"id": ["A user with this id does not exist."]}

    if user and not org_user:
        errors["user"] = {"id": ["A user with this id does not exist in this org."]}

    if phone_no_check:
        errors["phoneNo"] = ["This caller id is already assigned."]

    if errors:
        return response.validation_failed(errors)

    caller_id = caller_id_dao.create_caller_id(
        country=country,
        telephony_provider=telephony_provider,
        call_type=call_type,
        user=user,
        phone_no=phone_no,
        org=org,
        current_user=current_user,
    )
    caller_id_dao.create_caller_id_history(
        country=country,
        telephony_provider=telephony_provider,
        call_type=call_type,
        user=user,
        phone_no=phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_INSERT,
        org=org,
        current_user=current_user,
    )

    res = caller_id_schemas.org_caller_id_schema.dump(caller_id)
    return response.success(res)


def update_org_caller_id(org_id, caller_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    caller_id_obj = caller_id_dao.get_caller_id_with_id(caller_id, org=org)

    if not caller_id_obj:
        return response.not_found()

    try:
        data = caller_id_schemas.update_caller_id_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    phone_no = data.get("phone_no")

    caller_id_obj_with_same_phone_no = caller_id_dao.get_caller_id_with_phone_no(
        phone_no, for_org=True
    )

    errors = {}

    if (
        caller_id_obj_with_same_phone_no
        and caller_id_obj
        and caller_id_obj.id != caller_id_obj_with_same_phone_no.id
    ):
        errors["phoneNo"] = ["This caller id is already assigned."]

    if errors:
        return response.validation_failed(errors)

    caller_id = caller_id_dao.update_caller_id(caller_id_obj, phone_no, current_user)

    caller_id_dao.create_caller_id_history(
        country=caller_id_obj.country,
        telephony_provider=caller_id_obj.telephony_provider,
        call_type=caller_id_obj.call_type,
        user=caller_id_obj.user,
        phone_no=phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_UPDATE,
        org=org,
        current_user=current_user,
    )

    res = caller_id_schemas.org_caller_id_schema.dump(caller_id)
    return response.success(res)


def delete_org_caller_id(org_id, caller_id, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    caller_id_obj = caller_id_dao.get_caller_id_with_id(caller_id, org=org)

    if not caller_id_obj:
        return response.not_found()

    caller_id_dao.create_caller_id_history(
        country=caller_id_obj.country,
        telephony_provider=caller_id_obj.telephony_provider,
        call_type=caller_id_obj.call_type,
        user=caller_id_obj.user,
        phone_no=caller_id_obj.phone_no,
        action=constants.CALLER_ID_HISTORY_ACTION_DELETE,
        org=org,
        current_user=current_user,
    )
    caller_id_dao.delete_caller_id(caller_id_obj)
    res = {}
    return response.success(res)


def get_org_caller_ids(org_id):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    caller_id = caller_id_dao.get_caller_ids(org=org)
    res = caller_id_schemas.org_caller_id_schema.dump(caller_id, many=True)
    return response.success(res)


def get_org_caller_id(org_id, caller_id):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    caller_id = caller_id_dao.get_caller_id_with_id(caller_id, org=org)
    res = caller_id_schemas.org_caller_id_schema.dump(caller_id)
    return response.success(res)
