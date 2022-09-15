from ..models.main import FlowCategory


def get_all_flow_categories():
    return FlowCategory.query.all()


def get_flow_category_by_id(id):
    return FlowCategory.query.get(id)
