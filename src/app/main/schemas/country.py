from marshmallow import Schema, fields


class CountrySchema(Schema):
    id = fields.Integer(
        strict=True,
        required=True,
        error_messages={
            "required": "Id is required",
            "null": "Id is required",
            "invalid": "Id must be a valid number",
        },
    )
    name = fields.String(
        required=True,
        error_messages={
            "required": "Country name is required",
            "null": "Country name is required",
            "invalid": "Country name must be a string",
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


country_schema = CountrySchema(only=("id", "name", "country_code"))

create_country_schema = CountrySchema(only=("name", "country_code"))

update_country_schema = CountrySchema(only=("name", "country_code"))
