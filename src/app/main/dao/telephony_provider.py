from ..models.main import TelephonyProvider


def get_telephony_provider_with_id(telephony_provider_id):
    return TelephonyProvider.query.get(telephony_provider_id)


def get_all_telephony_providers():
    return TelephonyProvider.query.all()


def get_telephony_providers_with_ids(telephony_provider_ids):
    return TelephonyProvider.query.filter(
        TelephonyProvider.id.in_(telephony_provider_ids)
    ).all()
