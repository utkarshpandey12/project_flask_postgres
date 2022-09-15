from marshmallow import Schema, fields


class CampaignSchema(Schema):
    id = fields.Integer()
    name = fields.String()


campaign_schema = CampaignSchema(only=("id", "name"))
