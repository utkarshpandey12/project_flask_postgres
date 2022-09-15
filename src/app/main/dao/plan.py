import datetime

from sqlalchemy.orm import contains_eager

from ... import db
from ..models.main import Plan, PlanAttribute, PlanCountry, PlanFlowTemplate, PlanModule


def get_plan_with_id(plan_id):
    return Plan.query.get(plan_id)


def create_plan(name, start_on, end_on, org, current_user):
    now = datetime.datetime.now()
    plan = Plan(
        name=name,
        start_on=start_on,
        end_on=end_on,
        org=org,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(plan)
    db.session.flush()
    return plan


def update_plan(plan, start_on, end_on, current_user):
    now = datetime.datetime.now()
    plan.start_on = start_on
    plan.end_on = end_on
    plan.updated_at = now
    plan.updated_by_user = current_user
    db.session.add(plan)
    db.session.flush()
    return plan


def get_plan_modules_with_plan_id(plan_id):
    return (
        PlanModule.query.join(PlanModule.module)
        .options(contains_eager(PlanModule.module))
        .filter(PlanModule.plan_id == plan_id)
        .all()
    )


def delete_plan_modules_with_plan_id(plan_id):
    return PlanModule.query.filter(PlanModule.plan_id == plan_id).delete()


def delete_plan_attributes_with_plan_id(plan_id):
    return PlanAttribute.query.filter(PlanAttribute.plan_id == plan_id).delete()


def delete_plan_countries_with_plan_id(plan_id):
    return PlanCountry.query.filter(PlanCountry.plan_id == plan_id).delete()


def delete_plan_flow_templates_with_plan_id(plan_id):
    return PlanFlowTemplate.query.filter(PlanFlowTemplate.plan_id == plan_id).delete()


def create_plan_attributes(plan, attributes, int_values, bool_values):
    plan_attributes = []
    for attribute, int_value, bool_value in zip(attributes, int_values, bool_values):
        plan_attributes.append(
            PlanAttribute(
                plan=plan,
                attribute=attribute,
                int_value=int_value,
                bool_value=bool_value,
            )
        )
    db.session.add_all(plan_attributes)
    db.session.flush()
    return plan_attributes


def create_plan_modules(plan, modules):
    plan_modules = []
    for module in modules:
        plan_modules.append(PlanModule(plan=plan, module=module))
    db.session.add_all(plan_modules)
    db.session.flush()
    return plan_modules


def create_plan_flow_templates(plan, flow_templates):
    plan_flow_templates = []
    for flow_template in flow_templates:
        plan_flow_templates.append(
            PlanFlowTemplate(plan=plan, flow_template=flow_template)
        )
    db.session.add_all(plan_flow_templates)
    db.session.flush()
    return plan_flow_templates


def create_plan_countries(plan, countries, telephony_providers):
    plan_countries = []
    for country, telephony_provider in zip(countries, telephony_providers):
        plan_countries.append(
            PlanCountry(
                plan=plan, country=country, telephony_provider=telephony_provider
            )
        )
    db.session.add_all(plan_countries)
    db.session.flush()
    return plan_countries
