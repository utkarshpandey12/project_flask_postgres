from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf

from ..models import main as constants
from .country import CountrySchema
from .org import OrgSchema
from .telephony_provider import TelephonyProviderSchema
from .user import UserSchema


class CallerIdSchema(Schema):
    id = fields.Integer()
    org = fields.Nested(
        OrgSchema,
        required=True,
        error_messages={
            "required": "Org data is required",
            "null": "Org data is required",
        },
    )
    country = fields.Nested(
        CountrySchema,
        required=True,
        error_messages={
            "required": "Country data is required",
            "null": "Country data is required",
        },
    )
    telephony_provider = fields.Nested(
        TelephonyProviderSchema,
        data_key="telephonyProvider",
        required=True,
        error_messages={
            "required": "Telephony provider data is required",
            "null": "Telephony provider data is required",
        },
    )
    call_type = fields.String(
        data_key="callType",
        allow_none=True,
        validate=[
            OneOf(
                [
                    constants.CALLER_ID_CALL_TYPE_INITIAL,
                    constants.CALLER_ID_CALL_TYPE_FOLLOW_UP,
                ],
                error="Call type must be one of - {choices}.",
            )
        ],
        error_messages={
            "required": "Call type is required",
            "invalid": "Call type must be a string",
        },
    )
    user = fields.Nested(
        UserSchema,
        required=True,
        error_messages={
            "required": "User data is required",
            "null": "User data is required",
        },
    )
    phone_no = fields.String(
        data_key="phoneNo",
        required=True,
        validate=[
            Length(
                min=1,
                max=16,
                error="Phone no must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "required": "Phone no is required",
            "null": "Phone no is required",
            "invalid": "Phone no must be a string",
        },
    )


caller_id_schema = CallerIdSchema(
    only=(
        "id",
        "country.id",
        "country.name",
        "country.country_code",
        "telephony_provider.id",
        "telephony_provider.name",
        "phone_no",
    )
)

org_caller_id_schema = CallerIdSchema(
    only=(
        "id",
        "country.id",
        "country.name",
        "country.country_code",
        "telephony_provider.id",
        "telephony_provider.name",
        "call_type",
        "user.id",
        "user.name",
        "phone_no",
    )
)

create_caller_id_schema = CallerIdSchema(
    only=(
        "country.id",
        "telephony_provider.id",
        "phone_no",
    )
)

create_org_caller_id_schema = CallerIdSchema(
    only=(
        "country.id",
        "telephony_provider.id",
        "call_type",
        "user.id",
        "phone_no",
    )
)

update_caller_id_schema = CallerIdSchema(only=("phone_no",))
