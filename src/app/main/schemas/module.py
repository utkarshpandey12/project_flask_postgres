from marshmallow import Schema, fields


class ModuleSchema(Schema):
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


module_schema = ModuleSchema(only=("id", "name"))
