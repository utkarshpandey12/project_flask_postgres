from marshmallow import Schema, fields


class TelephonyProviderSchema(Schema):
    id = fields.Integer(
        strict=True,
        required=True,
        error_messages={
            "required": "Id is required",
            "null": "Id is required",
            "invalid": "Id must be a valid number",
        },
    )
    name = fields.String()
    identifier = fields.String()


telephony_provider_schema = TelephonyProviderSchema(
    only=(
        "id",
        "name",
    ),
)
