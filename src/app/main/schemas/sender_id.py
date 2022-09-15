from marshmallow import Schema, fields
from marshmallow.validate import Length

from .country import CountrySchema
from .sms_provider import SmsProviderSchema


class SenderIdSchema(Schema):
    id = fields.Integer()
    country_id = fields.Integer(
        data_key="countryId",
        required=True,
        error_messages={
            "required": "Country Id is required",
            "null": "Country Id is required",
            "invalid": "Country Id must be a valid number",
        },
    )
    country = fields.Nested(CountrySchema)
    sms_provider_id = fields.Integer(
        data_key="smsProviderId",
        required=True,
        error_messages={
            "required": "Sms Provider Id is required",
            "null": "Sms Provider Id is required",
            "invalid": "Sms Provider Id must be a valid number",
        },
    )
    sms_provider = fields.Nested(SmsProviderSchema, data_key="smsProvider")
    value = fields.String(
        data_key="value",
        required=True,
        validate=[
            Length(
                min=1,
                max=12,
                error="Sender Id must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "required": "Sender Id is required",
            "null": "Sender Id is required",
            "invalid": "Sender Id must be a string",
        },
    )


sender_id_schema = SenderIdSchema(
    only=(
        "id",
        "country.id",
        "country.name",
        "country.country_code",
        "sms_provider.id",
        "sms_provider.name",
        "value",
    )
)

create_sender_id_schema = SenderIdSchema(
    only=("country_id", "sms_provider_id", "value")
)

update_sender_id_schema = SenderIdSchema(only=("value",))
