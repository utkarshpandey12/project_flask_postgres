from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from ..models import main as constants
from .org import OrgSchema
from .plan import PlanSchema


class SubscriptionSchema(Schema):
    id = fields.Integer()
    org = fields.Nested(
        OrgSchema,
        required=True,
        error_messages={
            "required": "org data is required",
            "null": "org data is required",
        },
    )
    plan = fields.Nested(PlanSchema)
    start_on = fields.Date(
        data_key="startOn",
        required=True,
        error_messages={
            "required": "Start Date   is required",
            "null": "Start Date is required",
            "invalid": "Start Date must be a valid date ",
        },
    )
    end_on = fields.Date(
        data_key="endOn",
        required=True,
        error_messages={
            "required": "End Date is required",
            "null": "End Date is required",
            "invalid": "End Date must be a valid date",
        },
    )
    renewal_grace_period_days = fields.Integer(
        strict=True,
        data_key="renewalGracePeriodDays",
        required=True,
        error_messages={
            "required": "Renewal Grace Period (in days) is required",
            "null": "Renewal Grace Period (in days) is required",
            "invalid": "Renewal Grace Period (in days) must be a valid number",
        },
    )


create_update_subscription_schema = SubscriptionSchema(
    only=("start_on", "end_on", "renewal_grace_period_days")
)

subscription_schema = SubscriptionSchema(
    only=(
        "id",
        "org.id",
        "org.name",
        "start_on",
        "end_on",
        "renewal_grace_period_days",
        "plan.id",
        "plan.name",
    )
)

subscription_details_schema = SubscriptionSchema(
    only=(
        "id",
        "org.id",
        "org.name",
        "start_on",
        "end_on",
        "renewal_grace_period_days",
        "plan.id",
        "plan.name",
        "plan.plan_modules.id",
        "plan.plan_modules.module.id",
        "plan.plan_modules.module.name",
        "plan.plan_attributes.attribute.id",
        "plan.plan_attributes.attribute.name",
        "plan.plan_attributes.attribute.attribute_type",
        "plan.plan_attributes.int_value",
        "plan.plan_attributes.bool_value",
        "plan.plan_flow_templates.flow_template.id",
        "plan.plan_flow_templates.flow_template.name",
        "plan.plan_flow_templates.flow_template.status",
        "plan.plan_flow_templates.flow_template.flow_category.id",
        "plan.plan_flow_templates.flow_template.flow_category.name",
        "plan.plan_countries.country.id",
        "plan.plan_countries.country.name",
        "plan.plan_countries.country.country_code",
        "plan.plan_countries.telephony_provider.id",
        "plan.plan_countries.telephony_provider.name",
    )
)


class InviteTransactionSchema(Schema):
    id = fields.Integer()
    org = fields.Nested(OrgSchema)
    subscription = fields.Nested(SubscriptionSchema)
    txn_on = fields.Date(data_key="txnOn")
    txn_type = fields.String(
        data_key="txnType",
        required=True,
        validate=[
            OneOf(
                [
                    constants.INVITE_TRANSACTION_TYPE_ADJUSTMENT,
                    constants.INVITE_TRANSACTION_TYPE_TOP_UP,
                    constants.INVITE_TRANSACTION_TYPE_SUBSCRIPTION,
                ],
                error="Transaction type must be one of - {choices}.",
            )
        ],
        error_messages={
            "required": "Transaction type is required",
            "null": "Transaction type is required",
            "invalid": "Transaction type must be a string",
        },
    )
    amount = fields.Integer(
        strict=True,
        required=True,
        error_messages={
            "required": "Amount is required",
            "null": "Amount is required",
            "invalid": "Amount must be a valid number",
        },
    )


create_invite_transaction_schema = InviteTransactionSchema(
    only=(
        "txn_type",
        "amount",
    )
)

invite_transaction_schema = InviteTransactionSchema(
    only=(
        "id",
        "txn_on",
        "txn_type",
        "amount",
    )
)


class InviteBalanceSchema(Schema):
    id = fields.Integer()
    amount = fields.Integer()


invite_balance_schema = InviteBalanceSchema(only=("amount",))
