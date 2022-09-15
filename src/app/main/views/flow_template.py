import json

from flask import abort, g, request
from flask_login import login_required

from ...decorators.permission import sys_admin_required
from ...decorators.transaction import transaction
from .. import main
from ..api import flow_template as flow_template_api


@main.route("/v1/fields/", methods=["GET"])
@login_required
@sys_admin_required()
def get_fields():
    return flow_template_api.get_fields()


@main.route("/v1/flow-templates/", methods=["GET"])
@login_required
@sys_admin_required()
def get_all_flow_templates():
    return flow_template_api.get_all_flow_templates()


@main.route("/v1/flow-templates/<int:flow_template_id>/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template(flow_template_id):
    return flow_template_api.get_flow_template(flow_template_id, g.current_user)


@main.route("/v1/flow-templates/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_flow_template():
    return flow_template_api.create_flow_template(request.json, g.current_user)


@main.route("/v1/flow-templates/<int:flow_template_id>/fields/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_fields(flow_template_id):
    return flow_template_api.get_flow_template_fields(flow_template_id, g.current_user)


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/fields/<int:flow_template_field_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_flow_template_field(flow_template_id, flow_template_field_id):
    return flow_template_api.get_flow_template_field(
        flow_template_id, flow_template_field_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/fields/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_field(flow_template_id):
    return flow_template_api.create_flow_template_field(
        flow_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/fields/<int:flow_template_field_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_flow_template_field(flow_template_id, flow_template_field_id):
    return flow_template_api.update_flow_template_field(
        flow_template_id, flow_template_field_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/fields/<int:flow_template_field_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_flow_template_field(flow_template_id, flow_template_field_id):
    return flow_template_api.delete_flow_template_field(
        flow_template_id, flow_template_field_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/dynamic-option-attributes/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
@transaction()
def get_flow_template_dynamic_option_attributes(flow_template_id):
    return flow_template_api.get_flow_template_dynamic_option_attributes(
        flow_template_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/statuses/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_statuses(flow_template_id):
    return flow_template_api.get_flow_template_statuses(
        flow_template_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/statuses/<int:flow_template_status_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_flow_template_status(flow_template_id, flow_template_status_id):
    return flow_template_api.get_flow_template_status(
        flow_template_id, flow_template_status_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/statuses/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_status(flow_template_id):
    return flow_template_api.create_flow_template_status(
        flow_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/statuses/<int:flow_template_status_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_flow_template_status(flow_template_id, flow_template_status_id):
    return flow_template_api.update_flow_template_status(
        flow_template_id, flow_template_status_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/statuses/<int:flow_template_status_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_flow_template_status(flow_template_id, flow_template_status_id):
    return flow_template_api.delete_flow_template_status(
        flow_template_id, flow_template_status_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/messages/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_messages(flow_template_id):
    org_id = request.args.get("orgId")
    return flow_template_api.get_flow_template_messages(
        flow_template_id, org_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/messages/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_message(flow_template_id):
    message_data = None

    try:
        message_data_str = request.form.get("messageData")
        message_data = json.loads(message_data_str)
    except TypeError:
        abort(400)
    except json.decoder.JSONDecodeError:
        abort(400)

    return flow_template_api.create_flow_template_message(
        flow_template_id, message_data, request.files.get("audioFile"), g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/email-templates/", methods=["GET"]
)
@login_required
@sys_admin_required()
def get_flow_template_email_templates(flow_template_id):
    org_id = request.args.get("orgId")
    return flow_template_api.get_flow_template_email_templates(
        flow_template_id, org_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/"
    "email-templates/<int:email_template_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_flow_template_email_template(flow_template_id, email_template_id):
    return flow_template_api.get_flow_template_email_template(
        flow_template_id, email_template_id
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/email-templates/", methods=["POST"]
)
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_email_template(flow_template_id):
    return flow_template_api.create_flow_template_email_template(
        flow_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/"
    "email-templates/<int:email_template_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_flow_template_email_template(flow_template_id, email_template_id):
    return flow_template_api.update_flow_template_email_template(
        flow_template_id, email_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/"
    "email-templates/<int:email_template_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_flow_template_email_template(flow_template_id, email_template_id):
    return flow_template_api.delete_flow_template_email_template(
        flow_template_id, email_template_id
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/sms-templates/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_sms_templates(flow_template_id):
    org_id = request.args.get("orgId")
    return flow_template_api.get_flow_template_sms_templates(
        flow_template_id, org_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/sms-templates/<int:sms_template_id>/",
    methods=["GET"],
)
@login_required
@sys_admin_required()
def get_flow_template_sms_template(flow_template_id, sms_template_id):
    return flow_template_api.get_flow_template_sms_template(
        flow_template_id, sms_template_id
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/sms-templates/", methods=["POST"]
)
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_sms_template(flow_template_id):
    return flow_template_api.create_flow_template_sms_template(
        flow_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/sms-templates/<int:sms_template_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_flow_template_sms_template(flow_template_id, sms_template_id):
    return flow_template_api.update_flow_template_sms_template(
        flow_template_id, sms_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/sms-templates/<int:sms_template_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_flow_template_sms_template(flow_template_id, sms_template_id):
    return flow_template_api.delete_flow_template_sms_template(
        flow_template_id, sms_template_id
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/flows/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_flows(flow_template_id):
    return flow_template_api.get_flow_template_flows(flow_template_id, g.current_user)


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/", methods=["GET"]
)
@login_required
@sys_admin_required()
def get_flow_template_flow_details(flow_template_id, flow_id):
    return flow_template_api.get_flow_template_flow_details(
        flow_template_id, flow_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/pages/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_pages(flow_template_id):
    return flow_template_api.get_flow_template_pages(flow_template_id, g.current_user)


@main.route("/v1/flow-templates/<int:flow_template_id>/settings/", methods=["GET"])
@login_required
@sys_admin_required()
def get_flow_template_settings(flow_template_id):
    return flow_template_api.get_flow_template_settings(
        flow_template_id, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/settings/", methods=["PUT"])
@login_required
@sys_admin_required()
@transaction()
def upload_flow_template_settings(flow_template_id):
    return flow_template_api.update_flow_template_settings(
        flow_template_id, request.json, g.current_user
    )


@main.route("/v1/flow-templates/<int:flow_template_id>/flows/", methods=["POST"])
@login_required
@sys_admin_required()
@transaction()
def create_flow_template_flow(flow_template_id):
    return flow_template_api.create_flow_template_flow(
        flow_template_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/", methods=["GET"]
)
@login_required
@sys_admin_required()
def get_flow_template_steps(flow_template_id, flow_id):
    return flow_template_api.get_flow_template_steps(
        flow_template_id, flow_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/send-email/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_send_email_step(flow_template_id, flow_id):
    return flow_template_api.create_send_email_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/send-email/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_send_email_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_send_email_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/send-sms/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_send_sms_step(flow_template_id, flow_id):
    return flow_template_api.create_send_sms_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/send-sms/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_send_sms_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_send_sms_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/delay/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_delay_step(flow_template_id, flow_id):
    return flow_template_api.create_delay_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/delay/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_delay_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_delay_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/questions/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_questions_step(flow_template_id, flow_id):
    return flow_template_api.create_questions_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/questions/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_questions_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_questions_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/play-message/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_play_message_step(flow_template_id, flow_id):
    return flow_template_api.create_play_message_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/play-message/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_play_message_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_play_message_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/get-input/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_get_input_step(flow_template_id, flow_id):
    return flow_template_api.create_get_input_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/get-input/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_get_input_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_get_input_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/record-audio/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_record_audio_step(flow_template_id, flow_id):
    return flow_template_api.create_record_audio_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/record-audio/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_record_audio_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_record_audio_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/set-status/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_set_status_step(flow_template_id, flow_id):
    return flow_template_api.create_set_status_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/set-status/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_set_status_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_set_status_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/call/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_call_step(flow_template_id, flow_id):
    return flow_template_api.create_call_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/call/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_call_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_call_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/hang-up/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_hang_up_step(flow_template_id, flow_id):
    return flow_template_api.create_hang_up_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/hang-up/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_hang_up_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_hang_up_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/go-to-flow/",
    methods=["POST"],
)
@login_required
@sys_admin_required()
@transaction()
def create_go_to_flow_step(flow_template_id, flow_id):
    return flow_template_api.create_go_to_flow_step(
        flow_template_id, flow_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/"
    "steps/go-to-flow/<step_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_go_to_flow_step(flow_template_id, flow_id, step_id):
    return flow_template_api.update_go_to_flow_step(
        flow_template_id, flow_id, step_id, request.json, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/steps/<step_id>/",
    methods=["DELETE"],
)
@login_required
@sys_admin_required()
@transaction()
def delete_step(flow_template_id, flow_id, step_id):
    return flow_template_api.delete_step(
        flow_template_id, flow_id, step_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/events/", methods=["GET"]
)
@login_required
@sys_admin_required()
def get_flow_template_events(flow_template_id, flow_id):
    return flow_template_api.get_flow_template_events(
        flow_template_id, flow_id, g.current_user
    )


@main.route(
    "/v1/flow-templates/<int:flow_template_id>/flows/<flow_id>/events/<event_id>/",
    methods=["PUT"],
)
@login_required
@sys_admin_required()
@transaction()
def update_event(flow_template_id, flow_id, event_id):
    return flow_template_api.update_event(
        flow_template_id, flow_id, event_id, request.json, g.current_user
    )
