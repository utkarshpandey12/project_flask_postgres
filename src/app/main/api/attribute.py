from ...utils import response
from ..dao import attribute as attribute_dao
from ..schemas import attribute as attribute_schemas


def get_all_attributes():
    attribute = attribute_dao.get_all_attributes()
    res = attribute_schemas.attribute_schema.dump(attribute, many=True)
    return response.success(res)
