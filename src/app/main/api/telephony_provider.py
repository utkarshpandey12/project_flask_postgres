from ...utils import response
from ..dao import telephony_provider as telephony_provider_dao
from ..schemas import telephony_provider as telephony_provider_schemas


def get_all_telephony_providers():
    telephony_providers = telephony_provider_dao.get_all_telephony_providers()
    res = telephony_provider_schemas.telephony_provider_schema.dump(
        telephony_providers, many=True
    )
    return response.success(res)
