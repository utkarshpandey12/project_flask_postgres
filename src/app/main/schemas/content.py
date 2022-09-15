from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from ..models import main as constants


class EmailTemplateSchema(Schema):
    id = fields.Integer()
    org_id = fields.Integer(
        data_key="orgId",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Org Id is required",
            "invalid": "A valid Org Id is required",
        },
    )
    name = fields.String(required=True)
    description = fields.String(required=True, allow_none=True)
    email_format = fields.String(
        data_key="emailFormat",
        required=True,
        allow_none=True,
        validate=OneOf(
            [
                constants.EMAIL_FORMAT_TEXT,
                constants.EMAIL_FORMAT_HTML,
            ],
            error="Email Format must be one of - {choices}.",
        ),
    )
    subject = fields.String(required=True)
    body_text = fields.String(data_key="bodyText", required=True)
    body_html = fields.String(data_key="bodyHtml", required=True, allow_none=True)


email_template_schema = EmailTemplateSchema(
    only=(
        "id",
        "name",
        "description",
        "email_format",
        "subject",
        "body_text",
        "body_html",
    )
)

create_email_template_schema = EmailTemplateSchema(
    only=(
        "org_id",
        "name",
        "description",
        "email_format",
        "subject",
        "body_text",
        "body_html",
    )
)

update_email_template_schema = EmailTemplateSchema(
    only=(
        "description",
        "email_format",
        "subject",
        "body_text",
        "body_html",
    )
)


class SmsTemplateSchema(Schema):
    id = fields.Integer()
    org_id = fields.Integer(
        data_key="orgId",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Org Id is required",
            "invalid": "A valid Org Id is required",
        },
    )
    name = fields.String(required=True)
    description = fields.String(required=True, allow_none=True)
    message = fields.String(required=True)


sms_template_schema = SmsTemplateSchema(
    only=(
        "id",
        "name",
        "description",
        "message",
    )
)

create_sms_template_schema = SmsTemplateSchema(
    only=(
        "org_id",
        "name",
        "description",
        "message",
    )
)


update_sms_template_schema = SmsTemplateSchema(
    only=(
        "description",
        "message",
    )
)
