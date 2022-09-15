from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf

from ..models import main as constants


class RoleSchema(Schema):
    id = fields.Integer()

    name = fields.String(
        required=True,
        validate=[
            Length(
                min=2, max=30, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Role name is required",
            "null": "Role name is required",
            "invalid": "Role name must be a string",
        },
    )

    role_type = fields.String(
        data_key="roleType",
        required=True,
        validate=OneOf(
            [
                constants.ROLE_TYPE_ADMIN,
                constants.ROLE_TYPE_TRANSCRIBER,
            ],
            error="Role Type must be one of - {choices}.",
        ),
    )


role_schema = RoleSchema(only=("id", "name", "role_type"))

create_role_schema = RoleSchema(only=("name", "role_type"))

update_role_schema = RoleSchema(only=("name",))
