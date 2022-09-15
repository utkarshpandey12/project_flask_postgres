from ...utils import response
from ..dao import flow_category as flow_category_dao
from ..schemas import flow_category as flow_category_schemas


def get_all_flow_categories():
    flow_category = flow_category_dao.get_all_flow_categories()
    res = flow_category_schemas.flow_category_schema.dump(flow_category, many=True)
    return response.success(res)
