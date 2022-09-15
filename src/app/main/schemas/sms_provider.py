from marshmallow import Schema, fields


class SmsProviderSchema(Schema):
    id = fields.Integer()
    name = fields.String()


sms_provider_schema = SmsProviderSchema(only=("id", "name"))
