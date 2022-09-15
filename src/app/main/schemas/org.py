from marshmallow import Schema, fields
from marshmallow.validate import Length

from .timezone import TimezoneSchema
from .user import UserSchema


class OrgSchema(Schema):
    id = fields.Integer()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    display_name = fields.String(
        data_key="displayName",
        required=False,
        allow_none=True,
    )
    spoken_name = fields.String(
        data_key="spokenName",
        required=False,
        allow_none=True,
    )
    timezone = fields.Nested(
        TimezoneSchema,
        required=True,
        error_messages={
            "required": "Timezone data is required",
            "null": "Timezone data is required",
        },
    )
    owner = fields.Nested(
        UserSchema,
        required=True,
        error_messages={
            "required": "Owner data is required",
            "null": "Owner data is required",
        },
    )


create_org_schema = OrgSchema(
    only=(
        "name",
        "display_name",
        "spoken_name",
        "timezone",
        "owner.name",
        "owner.email",
        "owner.country_code",
        "owner.mobile_no",
    )
)


update_org_schema = OrgSchema(
    only=("name", "display_name", "spoken_name", "timezone.id")
)

org_schema = OrgSchema(
    only=(
        "id",
        "name",
        "display_name",
        "spoken_name",
        "timezone.id",
        "timezone.name",
    )
)


class OrgUserSchema(Schema):
    id = fields.Integer()
    org = fields.Nested(OrgSchema)
    user = fields.Nested(UserSchema)
    is_owner = fields.Boolean(data_key="isOwner")
    status = fields.String()


org_user_schema = OrgUserSchema(
    only=(
        "id",
        "user.id",
        "user.name",
        "is_owner",
    )
)
