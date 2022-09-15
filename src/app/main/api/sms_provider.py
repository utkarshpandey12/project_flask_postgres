from ...utils import response
from ..dao import sms_provider as sms_provider_dao
from ..schemas import sms_provider as sms_provider_schemas


def get_all_sms_providers():
    sms_providers = sms_provider_dao.get_all_sms_providers()
    res = sms_provider_schemas.sms_provider_schema.dump(sms_providers, many=True)
    return response.success(res)
