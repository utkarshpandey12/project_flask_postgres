from flask import current_app, jsonify, make_response


def success(data):
    return jsonify(data), 200


def invalid_request(errors):
    return jsonify(errors), 400


def unauthorized_error():
    res = make_response("401 Unauthorized\n")
    res.status_code = 401
    site_name = current_app.config["SITE_NAME"]
    res.headers["WWW-Authenticate"] = f'Token realm="{site_name}"'
    return res


def forbidden():
    return "", 403


def not_found():
    return "", 404


def validation_failed(errors):
    return jsonify(errors), 422
