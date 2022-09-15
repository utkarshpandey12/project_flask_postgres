from marshmallow import Schema, fields


class TimezoneSchema(Schema):
    id = fields.Integer(
        required=True,
        error_messages={
            "required": "Timezone id is required",
            "null": "Timezone id is required",
        },
    )
    name = fields.String(
        required=True,
        error_messages={
            "required": "Timezone name is required",
            "null": "Timezone name is required",
            "invalid": "Timezone name must be a string",
        },
    )
    identifier = fields.String(
        required=True,
        error_messages={
            "required": "Timezone identifier is required",
            "null": "Timezone identifier is required",
            "invalid": "Timezone identifier must be a string",
        },
    )
    other_identifiers = fields.List(
        fields.String(),
        data_key="otherIdentifiers",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Timezone other_identifiers is required",
            "invalid": "Timezone other_identifiers must be a list",
        },
    )


timezone_schema = TimezoneSchema(only=("id", "name", "identifier", "other_identifiers"))

create_timezone_schema = TimezoneSchema(
    only=("name", "identifier", "other_identifiers")
)
