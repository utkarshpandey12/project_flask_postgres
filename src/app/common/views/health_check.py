from app.common import common


@common.route("/", methods=["GET"])
def health_check():
    return ""
