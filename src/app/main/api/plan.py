from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import attribute as attribute_dao
from ..dao import country as country_dao
from ..dao import flow_template as flow_template_dao
from ..dao import module as module_dao
from ..dao import plan as plan_dao
from ..dao import telephony_provider as telephony_provider_dao
from ..models import main as constants
from ..schemas import plan as plan_schemas


def update_plan_modules(plan_id, data):
    plan = plan_dao.get_plan_with_id(plan_id)
    if not plan:
        return response.not_found()

    try:
        data = plan_schemas.update_plan_module_schema.load(data, many=True)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    errors = {}

    module_ids = []
    for module_data in data:
        module_ids.append(module_data.get("module").get("id"))
    modules = module_dao.get_modules_with_ids(module_ids)
    if len(module_ids) != len(modules):
        valid_module_ids = [module.id for module in modules]
        for index, module_id in enumerate(data):
            if module_id.get("module").get("id") not in valid_module_ids:
                errors[str(index)] = {
                    "module": {"id": ["Invalid module id - {}".format(module_id)]}
                }

    if errors:
        return response.validation_failed(errors)

    plan_dao.delete_plan_modules_with_plan_id(plan_id)

    plan_modules = plan_dao.create_plan_modules(plan, modules)
    res = plan_schemas.plan_module_schema.dump(plan_modules, many=True)
    return response.success(res)


def update_plan_attributes(plan_id, data):
    plan = plan_dao.get_plan_with_id(plan_id)
    if not plan:
        return response.not_found()

    try:
        data = plan_schemas.update_plan_attribute_schema.load(data, many=True)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    errors = {}
    attribute_ids = []
    int_values = []
    bool_values = []

    attributes = attribute_dao.get_all_attributes()
    attributes_by_id = {attribute.id: attribute for attribute in attributes}

    for index, attribute_data in enumerate(data):
        attribute_id = attribute_data.get("attribute").get("id")

        if attribute_id in attribute_ids:
            errors[str(index)] = {"attribute": ["Duplicate attribute id in data"]}
            continue

        attribute = attributes_by_id.get(attribute_id)

        if not attribute:
            errors[str(index)] = {
                "attribute": {"id": [f"Invalid attribute id - {attribute_id}"]}
            }
            continue

        int_value = attribute_data.get("int_value")
        bool_value = attribute_data.get("bool_value")

        if attribute.attribute_type == constants.ATTRIBUTE_TYPE_INTEGER:
            if int_value is None:
                attribute_error = errors.setdefault(str(index), {})
                attribute_error["intValue"] = ["Value is required"]
            if bool_value is not None:
                attribute_error = errors.setdefault(str(index), {})
                attribute_error["boolValue"] = [
                    "Boolean value must not be specified for integer attribute"
                ]
        elif attribute.attribute_type == constants.ATTRIBUTE_TYPE_BOOLEAN:
            if int_value is not None:
                attribute_error = errors.setdefault(str(index), {})
                attribute_error["intValue"] = [
                    "Integer value must not be specified for boolean attribute"
                ]
            if bool_value is None:
                attribute_error = errors.setdefault(str(index), {})
                attribute_error["boolValue"] = ["Value is required"]

        attribute_ids.append(attribute_id)
        int_values.append(int_value)
        bool_values.append(bool_value)

    if len(attribute_ids) != len(attributes):
        valid_attribute_ids = {attribute.id for attribute in attributes}
        missing_attribute_ids = valid_attribute_ids - set(attribute_ids)
        errors["message"] = f"Missing values for attributes - {missing_attribute_ids}"

    if errors:
        return response.validation_failed(errors)

    plan_dao.delete_plan_attributes_with_plan_id(plan_id)
    plan_attributes = plan_dao.create_plan_attributes(
        plan, attributes, int_values, bool_values
    )
    res = plan_schemas.plan_attribute_schema.dump(plan_attributes, many=True)
    return response.success(res)


def update_plan_flow_templates(plan_id, data):
    plan = plan_dao.get_plan_with_id(plan_id)
    if not plan:
        return response.not_found()

    try:
        data = plan_schemas.update_plan_flow_template_schema.load(data, many=True)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    errors = {}

    flow_template_ids = []
    for flow_template_data in data:
        flow_template_ids.append(flow_template_data.get("flow_template").get("id"))
    flow_templates = flow_template_dao.get_flow_templates_with_ids(flow_template_ids)
    if len(flow_template_ids) != len(flow_templates):
        valid_flow_template_ids = [flow_template.id for flow_template in flow_templates]
        for index, flow_template_id in enumerate(data):
            if (
                flow_template_id.get("flow_template").get("id")
                not in valid_flow_template_ids
            ):
                errors[str(index)] = {
                    "flow_template": {
                        "id": ["Invalid flow template id - {}".format(flow_template_id)]
                    }
                }

    if errors:
        return response.validation_failed(errors)

    plan_dao.delete_plan_flow_templates_with_plan_id(plan_id)

    plan_modules = plan_dao.create_plan_flow_templates(plan, flow_templates)

    res = plan_schemas.plan_flow_template_schema.dump(plan_modules, many=True)
    return response.success(res)


def update_plan_countries(plan_id, data):

    plan = plan_dao.get_plan_with_id(plan_id)

    if not plan:
        return response.not_found()

    try:
        data = plan_schemas.update_plan_country_schema.load(data, many=True)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    errors = {}
    country_ids = []
    telephony_provider_ids = []

    for index, plan_country_data in enumerate(data):
        country_id = plan_country_data.get("country").get("id")
        if country_id in country_ids:
            errors[str(index)] = {"country": ["Duplicate country id in data"]}
        country_ids.append(plan_country_data.get("country").get("id"))
        telephony_provider_ids.append(
            plan_country_data.get("telephony_provider").get("id")
        )

    countries = country_dao.get_countries_with_ids(country_ids)

    if len(country_ids) != len(countries):
        valid_country_ids = [country.id for country in countries]
        for index, plan_country_data in enumerate(data):
            if plan_country_data.get("country").get("id") not in valid_country_ids:
                errors[str(index)] = {
                    "country": {
                        "id": [
                            "Invalid country id - {}".format(
                                plan_country_data.get("country").get("id")
                            )
                        ]
                    }
                }

    telephony_providers = telephony_provider_dao.get_telephony_providers_with_ids(
        telephony_provider_ids
    )

    if len(telephony_provider_ids) != len(telephony_providers):
        valid_telephony_provider_ids = [
            telephony_provider.id for telephony_provider in telephony_providers
        ]
        for index, plan_country_data in enumerate(data):
            if (
                plan_country_data.get("telephony_provider").get("id")
                not in valid_telephony_provider_ids
            ):
                errors[str(index)] = {
                    "telephony_provider": {
                        "id": [
                            "Invalid telephony provider id - {}".format(
                                plan_country_data.get("telephony_provider").get("id")
                            )
                        ]
                    }
                }

    if errors:
        return response.validation_failed(errors)

    plan_dao.delete_plan_countries_with_plan_id(plan_id)

    country_id_with_obj = {country.id: country for country in countries}
    telephony_provider_id_with_obj = {
        telephony_provider.id: telephony_provider
        for telephony_provider in telephony_providers
    }

    countries_obj = []
    telephony_providers_obj = []

    for plan_country_data in data:
        country_obj = country_id_with_obj.get(
            plan_country_data.get("country").get("id")
        )
        telephony_provider_obj = telephony_provider_id_with_obj.get(
            plan_country_data.get("telephony_provider").get("id")
        )

        countries_obj.append(country_obj)
        telephony_providers_obj.append(telephony_provider_obj)

    plan_countries = plan_dao.create_plan_countries(
        plan, countries_obj, telephony_providers_obj
    )

    res = plan_schemas.plan_country_schema.dump(plan_countries, many=True)
    return response.success(res)
