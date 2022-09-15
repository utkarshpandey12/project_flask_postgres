import phonenumbers


def format_e164(country_code, mobile_no):
    return f"+{country_code}{mobile_no}"


def get_country_code(number_e164):
    p = phonenumbers.parse(number_e164)
    return p.country_code


def get_phone_number(number_e164):
    p = phonenumbers.parse(number_e164)
    return p.national_number
