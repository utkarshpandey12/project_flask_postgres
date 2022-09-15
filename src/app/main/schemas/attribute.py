from marshmallow import Schema, fields


class AttributeSchema(Schema):
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
    attribute_type = fields.String(data_key="attributeType")


attribute_schema = AttributeSchema(only=("id", "name", "attribute_type"))
