from marshmallow import Schema, fields

from .attribute import AttributeSchema
from .country import CountrySchema
from .flow_template import FlowTemplateSchema
from .module import ModuleSchema
from .org import OrgSchema
from .telephony_provider import TelephonyProviderSchema


class PlanSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    org = fields.Nested(OrgSchema)
    start_on = fields.Date()
    end_on = fields.Date()
    plan_modules = fields.Nested("PlanModuleSchema", data_key="modules", many=True)
    plan_attributes = fields.Nested(
        "PlanAttributeSchema", data_key="attributes", many=True
    )
    plan_flow_templates = fields.Nested(
        "PlanFlowTemplateSchema", data_key="flowTemplates", many=True
    )
    plan_countries = fields.Nested("PlanCountrySchema", data_key="countries", many=True)


class PlanAttributeSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    plan = fields.Nested(PlanSchema)
    attribute = fields.Nested(
        AttributeSchema,
        required=True,
        error_messages={
            "required": "Attribute data is required",
            "null": "Attribute data is required",
        },
    )
    int_value = fields.Integer(
        data_key="intValue",
        required=True,
        allow_none=True,
        strict=True,
        error_messages={
            "required": "intValue is required",
            "null": "intValue is required",
            "invalid": "intValue must be a number",
        },
    )
    bool_value = fields.Boolean(
        data_key="boolValue",
        required=True,
        allow_none=True,
        strict=True,
        error_messages={
            "required": "boolValue is required",
            "null": "boolValue is required",
            "invalid": "boolValue must be a boolean",
        },
    )


update_plan_attribute_schema = PlanAttributeSchema(
    only=("attribute.id", "int_value", "bool_value")
)

plan_attribute_schema = PlanAttributeSchema(
    only=("id", "attribute.id", "attribute.name")
)


class PlanFlowTemplateSchema(Schema):
    id = fields.Integer()
    plan = fields.Nested(PlanSchema)
    flow_template = fields.Nested(
        FlowTemplateSchema,
        data_key="flowTemplate",
        required=True,
        error_messages={
            "required": "Flow Template data is required",
            "null": "Flow Template data is required",
        },
    )


update_plan_flow_template_schema = PlanFlowTemplateSchema(only=("flow_template.id",))

plan_flow_template_schema = PlanFlowTemplateSchema(
    only=("id", "flow_template.id", "flow_template.name")
)


class PlanModuleSchema(Schema):
    id = fields.Integer()
    module = fields.Nested(
        ModuleSchema,
        required=True,
        error_messages={
            "required": "Module data is required",
            "null": "Module data is required",
        },
    )


update_plan_module_schema = PlanModuleSchema(only=("module",))

plan_module_schema = PlanModuleSchema(only=("id", "module.id", "module.name"))


class PlanCountrySchema(Schema):
    id = fields.Integer()
    plan = fields.Nested(PlanSchema)
    country = fields.Nested(
        CountrySchema,
        required=True,
        error_messages={
            "required": "Country data is required",
            "null": "Country data is required",
        },
    )
    telephony_provider = fields.Nested(
        TelephonyProviderSchema,
        data_key="telephonyProvider",
        required=True,
        error_messages={
            "required": "Telephony Provider data is required",
            "null": "Telephony Provider data is required",
        },
    )


update_plan_country_schema = PlanCountrySchema(
    only=("country.id", "telephony_provider.id")
)

plan_country_schema = PlanCountrySchema(
    only=(
        "country.id",
        "country.name",
        "country.country_code",
        "telephony_provider.id",
        "telephony_provider.name",
    )
)
