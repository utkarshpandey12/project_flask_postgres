from ..models.main import SmsProvider


def get_sms_provider_with_id(sms_provider_id):
    return SmsProvider.query.get(sms_provider_id)


def get_all_sms_providers():
    return SmsProvider.query.all()
