from ...utils import response
from ..dao import module as module_dao
from ..schemas import module as module_schemas


def get_all_modules():
    module = module_dao.get_all_modules()
    res = module_schemas.module_schema.dump(module, many=True)
    return response.success(res)
