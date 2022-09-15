import json

from flask import abort, g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import recording_instruction as recording_instruction_api


@main.route("/v1/recording-instructions/", methods=["GET"])
@login_required
@sys_admin_required()
def get_recording_instructions():
    return recording_instruction_api.get_recording_instructions()


@main.route("/v1/recording-instructions/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_recording_instruction():
    data = None

    try:
        data_str = request.form.get("data")
        data = json.loads(data_str)
    except TypeError:
        abort(400)
    except json.decoder.JSONDecodeError:
        abort(400)

    return recording_instruction_api.create_recording_instruction(
        data, request.files.get("audioFile"), g.current_user
    )
