from marshmallow import Schema, fields
from marshmallow.validate import Length


class LanguageSchema(Schema):
    id = fields.Integer()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=50, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    identifier = fields.String(
        required=True,
        validate=[
            Length(
                min=1,
                max=50,
                error="Identifier must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "required": "Identifier is required",
            "null": "Identifier is required",
            "invalid": "Identifier must be a string",
        },
    )


language_schema = LanguageSchema(only=("id", "name", "identifier"))

create_language_schema = LanguageSchema(only=("name", "identifier"))

update_language_schema = LanguageSchema(only=("name", "identifier"))
