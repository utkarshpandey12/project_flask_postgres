from marshmallow.exceptions import ValidationError

from ...utils import crypto, job, phone_number, response
from ..dao import org as org_dao
from ..dao import subscription as subscription_dao
from ..dao import timezone as timezone_dao
from ..dao import user as user_dao
from ..models import main as constants
from ..schemas import org as org_schemas


def create_org(data, current_user):

    try:
        data = org_schemas.create_org_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    display_name = data.get("display_name")
    spoken_name = data.get("spoken_name")
    timezone_id = data.get("timezone").get("id")
    owner_data = data.get("owner")
    owner_name = owner_data.get("name")
    email = owner_data.get("email")
    country_code = owner_data.get("country_code")
    mobile_no = owner_data.get("mobile_no")
    mobile = phone_number.format_e164(country_code, mobile_no)

    org_check = org_dao.get_org_with_name(name)
    owner_email_check = user_dao.get_user_with_email(email)
    owner_mobile_no_check = user_dao.get_user_with_mobile(mobile)
    timezone = timezone_dao.get_timezone_with_id(timezone_id)

    errors = {}

    if org_check:
        errors["name"] = ["An org with this name already exists."]

    if owner_email_check:
        owner_errors = errors.setdefault("owner", {})
        owner_errors["email"] = ["A user with this email address already exists."]

    if owner_mobile_no_check:
        owner_errors = errors.setdefault("owner", {})
        owner_errors["mobileNo"] = ["A user with this mobile number already exists."]

    if not timezone:
        errors["timezone"] = {"id": ["Invalid timezone id."]}

    if errors:
        return response.validation_failed(errors)

    org = org_dao.create_org(name, display_name, spoken_name, timezone, current_user)

    password = crypto.generate_random_string(length=6)
    owner = user_dao.create_user(
        owner_name,
        email,
        password,
        mobile,
        must_change_password=True,
        is_email_verified=True,
        is_sys_admin=False,
        current_user=current_user,
    )

    subscription_dao.create_org_invite_balance(org, 0)
    subscription_dao.create_user_invite_balance(org, owner, 0)

    admin_role = user_dao.create_role(
        "Administrator", constants.ROLE_TYPE_CUSTOMER, org, current_user
    )
    user_dao.create_role("Recruiter", constants.ROLE_TYPE_CUSTOMER, org, current_user)
    user_dao.create_user_role(owner, admin_role, org, current_user)
    org_dao.create_org_user(owner, is_owner=True, org=org, current_user=current_user)
    job.queue_job(
        name="send_email",
        params={
            "subject": "Welcome to Callify",
            "body": "Your account has been created",
        },
        queue=job.JOB_QUEUE_DEFAULT,
    )

    res = org_schemas.org_schema.dump(org)
    return response.success(res)


def get_all_orgs():
    org = org_dao.get_all_orgs()
    res = org_schemas.org_schema.dump(
        org,
        many=True,
    )
    return response.success(res)


def get_org_details(org_id):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()
    res = org_schemas.org_schema.dump(org)
    return response.success(res)


def update_org(org_id, data, current_user):
    org = org_dao.get_org_with_id(org_id)

    if not org:
        return response.not_found()

    try:
        data = org_schemas.update_org_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    display_name = data.get("display_name")
    spoken_name = data.get("spoken_name")
    timezone_id = data.get("timezone").get("id")
    timezone = timezone_dao.get_timezone_with_id(timezone_id)
    errors = {}

    if not timezone:
        errors["timezone"] = {"id": ["Invalid timezone id."]}

    if errors:
        return response.validation_failed(errors)

    org = org_dao.update_org(
        name, display_name, spoken_name, timezone, org, current_user
    )
    res = org_schemas.org_schema.dump(org)
    return response.success(res)


def get_org_user_details(org_id):
    org = org_dao.get_org_with_id(org_id)
    if not org:
        return response.not_found()

    org_user = org_dao.get_org_user_details_with_org(org)
    if not org_user:
        return response.not_found()

    res = org_schemas.org_user_schema.dump(org_user, many=True)
    return response.success(res)
