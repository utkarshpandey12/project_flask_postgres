import shortuuid


def generate_random_string(length):
    return shortuuid.ShortUUID().random(length)
