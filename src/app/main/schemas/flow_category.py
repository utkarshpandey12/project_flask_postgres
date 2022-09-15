from marshmallow import Schema, fields


class FlowCategorySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    icon_url = fields.String(data_key="iconUrl")
    sequence = fields.Integer()


flow_category_schema = FlowCategorySchema(
    only=("id", "name", "description", "icon_url", "sequence"),
)
