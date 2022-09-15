from marshmallow import Schema, fields
from marshmallow.validate import ContainsOnly, Length

from .role import RoleSchema


class UserSchema(Schema):
    id = fields.Integer(allow_none=True)
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=70, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    email = fields.Email(
        required=True,
        validate=[
            Length(
                min=1, max=254, error="Email must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Email is required",
            "null": "Email is required",
            "invalid": "A valid email address is required",
        },
    )
    password = fields.String(
        required=True,
        load_only=True,
        validate=[
            Length(min=6, max=100, error="Password must be {min} or more characters"),
        ],
        error_messages={
            "required": "Password is required",
            "null": "Password is required",
            "invalid": "Password must be a string",
        },
    )
    country_code = fields.Integer(
        data_key="countryCode",
        required=True,
        error_messages={
            "required": "Country code is required",
            "null": "Country code is required",
            "invalid": "Country code must be an integer",
        },
    )
    mobile_no = fields.String(
        data_key="mobileNo",
        required=True,
        validate=[
            Length(
                min=1,
                max=10,
                error="Mobile number must be between {min} and {max} characters",
            ),
            ContainsOnly(
                ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                error="Mobile number must contain only digits",
            ),
        ],
        error_messages={
            "required": "Mobile number is required",
            "null": "Mobile number is required",
            "invalid": "Mobile number must be a string",
        },
    )
    roles = fields.Nested(RoleSchema, required=True, many=True)


create_update_user_schema = UserSchema(
    only=("name", "email", "mobile_no", "country_code", "roles.id")
)

user_schema = UserSchema(
    only=("id", "name", "email", "country_code", "mobile_no", "roles.id", "roles.name")
)
