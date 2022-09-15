import shortuuid
from marshmallow.exceptions import ValidationError
from slugify import slugify

from ...utils import response, s3
from ..dao import flow_category as flow_category_dao
from ..dao import flow_template as flow_template_dao
from ..dao import org as org_dao
from ..dao import recording_instruction as recording_instruction_dao
from ..models import flow_template as flow_template_constants
from ..models import main as constants
from ..models.flow_template import Template
from ..schemas import content as content_schemas
from ..schemas import flow_template as flow_template_schemas


def get_fields():
    fields = flow_template_dao.get_fields()
    res = flow_template_schemas.field_schema.dump(fields, many=True)
    return response.success(res)


def get_all_flow_templates():
    flow_template = flow_template_dao.get_all_flow_templates()
    res = flow_template_schemas.flow_template_schema.dump(flow_template, many=True)
    return response.success(res)


def get_flow_template(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    res = flow_template_schemas.flow_template_schema.dump(flow_template)
    return response.success(res)


def create_flow_template(data, current_user):
    try:
        data = flow_template_schemas.create_flow_template_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    version_identifier = data.get("version_identifier")
    description = data.get("description")
    flow_category_id = data.get("flow_category_id")

    errors = {}

    flow_category = flow_category_dao.get_flow_category_by_id(flow_category_id)

    if not flow_category:
        errors["flowCategoryId"] = ["Invalid flow category id."]

    flow_template_with_same_name_and_version = (
        flow_template_dao.get_flow_template_by_name_and_version_identifier(
            name, version_identifier
        )
    )

    if flow_template_with_same_name_and_version:
        errors[
            "message"
        ] = "A flow template with this name and version identifier already exists"

    if errors:
        return response.validation_failed(errors)

    flow_template = flow_template_dao.create_flow_template(
        name,
        version_identifier,
        description,
        flow_category,
        constants.FLOW_TEMPLATE_STATUS_DRAFT,
        current_user,
    )
    res = flow_template_schemas.flow_template_schema.dump(flow_template)
    return response.success(res)


def get_flow_template_fields(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    flow_template_fields = flow_template_dao.get_flow_template_fields(flow_template)
    res = flow_template_schemas.flow_template_field_schema.dump(
        flow_template_fields, many=True
    )
    return response.success(res)


def get_flow_template_field(flow_template_id, flow_template_field_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)

    if not flow_template:
        return response.not_found()

    flow_template_field = flow_template_dao.get_flow_template_field_with_id(
        flow_template, flow_template_field_id
    )

    if not flow_template_field:
        return response.not_found()

    res = flow_template_schemas.flow_template_field_schema.dump(flow_template_field)

    return response.success(res)


def create_flow_template_field(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    try:
        data = flow_template_schemas.create_flow_template_field_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    field_id = data.get("field_id")
    is_mandatory = data.get("is_mandatory")
    allow_multiple_values = data.get("allow_multiple_values")
    sequence = data.get("sequence")

    errors = {}

    field = flow_template_dao.get_field_with_id(field_id)

    if not field:
        errors["fieldId"] = ["Invalid field id."]

    if errors:
        return response.validation_failed(errors)

    flow_template_field = flow_template_dao.get_flow_template_field(
        flow_template, field
    )

    if flow_template_field:
        errors["fieldId"] = ["This field already exists in this flow template"]

    if errors:
        return response.validation_failed(errors)

    flow_template_field = flow_template_dao.create_flow_template_field(
        flow_template,
        field,
        is_mandatory,
        allow_multiple_values,
        sequence,
        current_user,
    )
    res = flow_template_schemas.flow_template_field_schema.dump(flow_template_field)
    return response.success(res)


def update_flow_template_field(
    flow_template_id, flow_template_field_id, data, current_user
):

    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    flow_template_field = flow_template_dao.get_flow_template_field_with_id(
        flow_template, flow_template_field_id
    )

    if not flow_template_field:
        return response.not_found()

    try:
        data = flow_template_schemas.update_flow_template_field_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    is_mandatory = data.get("is_mandatory")
    allow_multiple_values = data.get("allow_multiple_values")
    sequence = data.get("sequence")

    flow_template_field_updated = flow_template_dao.update_flow_template_field(
        flow_template,
        flow_template_field,
        is_mandatory,
        allow_multiple_values,
        sequence,
        current_user,
    )
    res = flow_template_schemas.flow_template_field_schema.dump(
        flow_template_field_updated
    )
    return response.success(res)


def delete_flow_template_field(flow_template_id, flow_template_field_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)

    if not flow_template:
        return response.not_found()

    flow_template_field = flow_template_dao.get_flow_template_field_with_id(
        flow_template, flow_template_field_id
    )

    if not flow_template_field:
        return response.not_found()

    flow_template_dao.delete_flow_template_field(flow_template_field)

    return response.success({})


def get_flow_template_dynamic_option_attributes(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    flow_template_fields = flow_template_dao.get_flow_template_fields(
        flow_template, field_type=constants.FIELD_TYPE_SCHEDULE
    )
    dynamic_option_attributes = []

    for flow_template_field in flow_template_fields:
        field = flow_template_field.field
        id = (
            f"{flow_template_constants.DYNAMIC_ATTRIBUTE_TYPE_CAMPAIGN_FIELD}."
            f"{field.field_type}."
            f"{field.identifier}."
            f"{flow_template_constants.DYNAMIC_ATTRIBUTE_DATA_TYPE_DATE}"
        )
        dynamic_option_attributes.append({"id": id, "name": f"{field.name} Dates"})
        id = (
            f"{flow_template_constants.DYNAMIC_ATTRIBUTE_TYPE_CAMPAIGN_FIELD}."
            f"{field.field_type}."
            f"{field.identifier}."
            f"{flow_template_constants.DYNAMIC_ATTRIBUTE_DATA_TYPE_TIME}"
        )
        dynamic_option_attributes.append({"id": id, "name": f"{field.name} Times"})

    res = flow_template_schemas.dynamic_attribute_schema.dump(
        dynamic_option_attributes, many=True
    )
    return response.success(res)


def get_flow_template_statuses(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    flow_template_statuses = flow_template_dao.get_flow_template_statuses(flow_template)
    res = flow_template_schemas.flow_template_status_schema.dump(
        flow_template_statuses, many=True
    )
    return response.success(res)


def get_flow_template_status(flow_template_id, flow_template_status_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)

    if not flow_template:
        return response.not_found()

    flow_template_status = flow_template_dao.get_flow_template_status_with_id(
        flow_template, flow_template_status_id
    )

    if not flow_template_status:
        return response.not_found()

    res = flow_template_schemas.flow_template_status_schema.dump(flow_template_status)

    return response.success(res)


def validate_flow_template_status(flow_template, flow_template_status, data):
    try:
        data = flow_template_schemas.create_update_flow_template_status_schema.load(
            data
        )
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_final = data.get("is_final")
    is_positive = data.get("is_positive")
    is_reattempt_allowed = data.get("is_reattempt_allowed")
    priority = data.get("priority")
    sequence = data.get("sequence")

    errors = {}

    existing_flow_template_status = (
        flow_template_dao.get_flow_template_status_with_name(flow_template, name)
    )

    if existing_flow_template_status is not None and (
        flow_template_status is None
        or existing_flow_template_status.id != flow_template_status.id
    ):
        errors["name"] = ["A status with this name already exists"]

    return (
        (
            name,
            is_final,
            is_positive,
            is_reattempt_allowed,
            priority,
            sequence,
        ),
        errors,
    )


def create_flow_template_status(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    valid_data, errors = validate_flow_template_status(flow_template, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_final, is_positive, is_reattempt_allowed, priority, sequence = valid_data

    flow_template_status = flow_template_dao.create_flow_template_status(
        flow_template,
        name,
        is_final,
        is_positive,
        is_reattempt_allowed,
        priority,
        sequence,
        current_user,
    )
    res = flow_template_schemas.flow_template_status_schema.dump(flow_template_status)
    return response.success(res)


def update_flow_template_status(
    flow_template_id, flow_template_status_id, data, current_user
):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    flow_template_status = flow_template_dao.get_flow_template_status_with_id(
        flow_template, flow_template_status_id
    )

    if not flow_template_status:
        return response.not_found()

    valid_data, errors = validate_flow_template_status(
        flow_template, flow_template_status, data
    )

    if errors:
        return response.validation_failed(errors)

    name, is_final, is_positive, is_reattempt_allowed, priority, sequence = valid_data

    flow_template_status_updated = flow_template_dao.update_flow_template_status(
        flow_template,
        flow_template_status,
        name,
        is_final,
        is_positive,
        is_reattempt_allowed,
        priority,
        sequence,
        current_user,
    )
    res = flow_template_schemas.flow_template_status_schema.dump(
        flow_template_status_updated
    )
    return response.success(res)


def delete_flow_template_status(
    flow_template_id, flow_template_status_id, current_user
):

    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)

    if not flow_template:
        return response.not_found()

    flow_template_status = flow_template_dao.get_flow_template_status_with_id(
        flow_template, flow_template_status_id
    )

    if not flow_template_status:
        return response.not_found()

    flow_template_dao.delete_flow_template_status(flow_template_status)

    return response.success({})


def get_flow_template_messages(flow_template_id, org_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    flow_template_messages = flow_template_dao.get_flow_template_messages(
        flow_template, org_id
    )
    res = flow_template_schemas.flow_template_message_schema.dump(
        flow_template_messages, many=True
    )
    return response.success(res)


S3_PATH_FLOW_TEMPLATE_MESSAGE = "audio/ft/{flow_template_id}/o/{org_id}/{file_name}"


def create_flow_template_message(flow_template_id, data, audio_file, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    try:
        data = flow_template_schemas.create_flow_template_message_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    org_id = data.get("org_id")
    name = data.get("name")
    description = data.get("description")
    message_type = data.get("message_type")
    message_text = data.get("message_text")
    attribute = data.get("attribute")
    recording_instruction_id = data.get("recording_instruction_id")
    sequence = data.get("sequence")

    errors = {}
    message_data_errors = {}
    errors["messageData"] = message_data_errors

    if message_type == constants.MESSAGE_TYPE_AUDIO_FROM_TEMPLATE:
        if not audio_file:
            errors["audioFile"] = ["Audio File is required"]
    else:
        if audio_file:
            errors["audioFile"] = [
                "Audio File must not be provided for the specified message type"
            ]

    if message_type == constants.MESSAGE_TYPE_AUDIO_FROM_CAMPAIGN:
        if not recording_instruction_id:
            message_data_errors["recordingInstructionId"] = [
                "Recording Instruction is required"
            ]

        if not sequence:
            errors["sequence"] = ["Sequence is required"]
    else:
        if recording_instruction_id:
            message_data_errors["recordingInstructionId"] = [
                "Recording Instruction must not be provided "
                "for the specified message type"
            ]

        if sequence:
            errors["sequence"] = [
                "Sequence must not to be provided " "for the specified message type"
            ]

    if message_type == constants.MESSAGE_TYPE_TEXT_TO_SPEECH_STATIC:
        if not message_text:
            message_data_errors["messageText"] = ["Message Text is required"]
    else:
        if message_text:
            message_data_errors["messageText"] = [
                "Message Text must not be provided for the specified message type"
            ]

    if message_type == constants.MESSAGE_TYPE_TEXT_TO_SPEECH_DYNAMIC:
        if not attribute:
            message_data_errors["attribute"] = ["Attribute is required"]
    else:
        if attribute:
            message_data_errors["attribute"] = [
                "Attribute must not be provided for the specified message type"
            ]

    if (
        message_type == constants.MESSAGE_TYPE_AUDIO_FROM_CAMPAIGN
        or message_type == constants.MESSAGE_TYPE_TEXT_TO_SPEECH_DYNAMIC
    ):
        if org_id:
            message_data_errors["orgId"] = [
                "Org-specific message cannot be created for the specified message type"
            ]

    if "audioFile" in errors or message_data_errors:
        if not message_data_errors:
            del errors["messageData"]
        return response.validation_failed(errors)

    file_name = None
    file_ext = None

    if audio_file:
        filename_parts = audio_file.filename.split(".")
        if len(filename_parts) != 2:
            errors["audioFile"] = ["Audio File must be of type wav or mp3"]
        else:
            file_name = filename_parts[0]
            file_ext = filename_parts[1].lower()
            if file_ext not in {"wav", "mp3"}:
                errors["audioFile"] = ["Audio File must be of type wav or mp3"]

    org = None
    if org_id:
        org = org_dao.get_org_with_id(org_id)

        if not org:
            message_data_errors["orgId"] = ["Invalid Org Id"]

        default_message = (
            flow_template_dao.get_flow_template_message_with_name_and_org_id(
                flow_template, name, org_id=None
            )
        )

        if not default_message:
            message_data_errors["name"] = [
                "A default message with this name doesn't exist. "
                "Please create the default message before creating "
                "an org-specific message."
            ]

    recording_instruction = None
    if recording_instruction_id:
        recording_instruction = (
            recording_instruction_dao.get_recording_instruction_with_id(
                recording_instruction_id
            )
        )

        if not recording_instruction:
            message_data_errors["recordingInstructionId"] = [
                "Invalid Recording Instruction Id"
            ]

    if "audioFile" in errors or message_data_errors:
        if not message_data_errors:
            del errors["messageData"]
        return response.validation_failed(errors)

    existing_message = flow_template_dao.get_flow_template_message_with_name_and_org_id(
        flow_template, name, org_id, case_insensitive=True
    )

    if existing_message:
        message_data_errors["name"] = [
            "A message with this name already exists in this flow template"
        ]

    if "audioFile" in errors or message_data_errors:
        if not message_data_errors:
            del errors["messageData"]
        return response.validation_failed(errors)

    audio_file_path = None

    if audio_file:
        file_name_slug = slugify(file_name)
        file_uuid = shortuuid.uuid()
        file_name_for_s3 = f"{file_name_slug}-{file_uuid}.{file_ext}"
        audio_file_path = S3_PATH_FLOW_TEMPLATE_MESSAGE.format(
            flow_template_id=flow_template_id,
            org_id=org_id if org_id else "default",
            file_name=file_name_for_s3,
        )
        s3.upload_audio_to_s3(audio_file_path, audio_file, is_private=False)

    message = flow_template_dao.create_flow_template_message(
        flow_template,
        org,
        name,
        description,
        message_type,
        message_text,
        attribute,
        audio_file_path,
        recording_instruction,
        sequence,
        current_user,
    )
    res = flow_template_schemas.flow_template_message_schema.dump(message)
    return response.success(res)


def get_flow_template_email_templates(flow_template_id, org_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    email_templates = flow_template_dao.get_flow_template_email_templates(
        flow_template, org_id
    )
    res = content_schemas.email_template_schema.dump(email_templates, many=True)
    return response.success(res)


def get_flow_template_email_template(flow_template_id, email_template_id):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    email_template = flow_template_dao.get_flow_template_email_template_with_id(
        flow_template, email_template_id
    )

    if not email_template:
        return response.not_found()

    res = content_schemas.email_template_schema.dump(email_template)
    return response.success(res)


def validate_flow_template_email_template(flow_template, email_template, data):
    try:
        schema = (
            content_schemas.create_email_template_schema
            if not email_template
            else content_schemas.update_email_template_schema
        )
        data = schema.load(data)
    except ValidationError as e:
        return None, e.messages

    org_id = data.get("org_id")
    name = data.get("name")
    description = data.get("description")
    email_format = data.get("email_format")
    subject = data.get("subject")
    body_text = data.get("body_text")
    body_html = data.get("body_html")

    errors = {}

    if email_format == constants.EMAIL_FORMAT_HTML and not body_html:
        errors["bodyHtml"] = ["Body (HTML) is required"]

    org = None
    if org_id:
        org = org_dao.get_org_with_id(org_id)

        if not org:
            errors["orgId"] = ["Invalid Org Id"]

        default_email_template = (
            flow_template_dao.get_flow_template_email_template_with_name_and_org_id(
                flow_template, name, org_id=None
            )
        )
        if not default_email_template:
            errors["name"] = [
                "A default email template with this name doesn't exist. "
                "Please create the default email template before creating "
                "an org-specific email template."
            ]

    if errors:
        return None, errors

    if name:
        existing_email_template = (
            flow_template_dao.get_flow_template_email_template_with_name_and_org_id(
                flow_template, name, org_id, case_insensitive=True
            )
        )
        if existing_email_template:
            errors["name"] = ["An email template with this name already exists"]

    if errors:
        return None, errors

    return (org, name, description, email_format, subject, body_text, body_html), errors


def create_flow_template_email_template(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    valid_data, errors = validate_flow_template_email_template(
        flow_template, None, data
    )

    if errors:
        return response.validation_failed(errors)

    org, name, description, email_format, subject, body_text, body_html = valid_data

    email_template = flow_template_dao.create_flow_template_email_template(
        flow_template,
        org,
        name,
        description,
        email_format,
        subject,
        body_text,
        body_html,
        current_user,
    )
    res = content_schemas.email_template_schema.dump(email_template)
    return response.success(res)


def update_flow_template_email_template(
    flow_template_id, email_template_id, data, current_user
):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    email_template = flow_template_dao.get_flow_template_email_template_with_id(
        flow_template, email_template_id
    )
    if not email_template:
        return response.not_found()

    valid_data, errors = validate_flow_template_email_template(
        flow_template, email_template, data
    )

    if errors:
        return response.validation_failed(errors)

    org, name, description, email_format, subject, body_text, body_html = valid_data

    flow_template_dao.update_flow_template_email_template(
        email_template,
        flow_template,
        description,
        email_format,
        subject,
        body_text,
        body_html,
        current_user,
    )
    res = content_schemas.update_email_template_schema.dump(email_template)
    return response.success(res)


def delete_flow_template_email_template(flow_template_id, email_template_id):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    email_template = flow_template_dao.get_flow_template_email_template_with_id(
        flow_template, email_template_id
    )

    if not email_template:
        return response.not_found()

    flow_template_dao.delete_flow_template_email_template(email_template)
    return response.success({})


def get_flow_template_sms_templates(flow_template_id, org_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    sms_templates = flow_template_dao.get_flow_template_sms_templates(
        flow_template, org_id
    )
    res = content_schemas.sms_template_schema.dump(sms_templates, many=True)
    return response.success(res)


def get_flow_template_sms_template(flow_template_id, sms_template_id):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    sms_template = flow_template_dao.get_flow_template_sms_template_with_id(
        flow_template, sms_template_id
    )
    if not sms_template:
        return response.not_found()

    res = content_schemas.sms_template_schema.dump(sms_template)
    return response.success(res)


def validate_flow_template_sms_template(flow_template, sms_template, data):
    try:
        schema = (
            content_schemas.create_sms_template_schema
            if not sms_template
            else content_schemas.update_sms_template_schema
        )
        data = schema.load(data)
    except ValidationError as e:
        return None, e.messages

    org_id = data.get("org_id")
    name = data.get("name")
    description = data.get("description")
    message = data.get("message")

    errors = {}

    org = None
    if org_id:
        org = org_dao.get_org_with_id(org_id)

        if not org:
            errors["orgId"] = ["Invalid Org Id"]

        default_sms_template = (
            flow_template_dao.get_flow_template_sms_template_with_name_and_org_id(
                flow_template, name, org_id=None
            )
        )

        if not default_sms_template:
            errors["name"] = [
                "A default SMS template with this name doesn't exist. "
                "Please create the default SMS template before creating "
                "an org-specific SMS template."
            ]

    if errors:
        return None, errors

    if name:
        existing_sms_template = (
            flow_template_dao.get_flow_template_sms_template_with_name_and_org_id(
                flow_template, name, org_id, case_insensitive=True
            )
        )
        if existing_sms_template:
            errors["name"] = ["A SMS template with this name already exists"]

    if errors:
        return None, errors

    return (org, name, description, message), errors


def create_flow_template_sms_template(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    valid_data, errors = validate_flow_template_sms_template(flow_template, None, data)

    if errors:
        return response.validation_failed(errors)

    org, name, description, message = valid_data

    sms_template = flow_template_dao.create_flow_template_sms_template(
        flow_template, org, name, description, message, current_user
    )
    res = content_schemas.sms_template_schema.dump(sms_template)
    return response.success(res)


def update_flow_template_sms_template(
    flow_template_id, sms_template_id, data, current_user
):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    sms_template = flow_template_dao.get_flow_template_sms_template_with_id(
        flow_template, sms_template_id
    )
    if not sms_template:
        return response.not_found

    valid_data, errors = validate_flow_template_sms_template(
        flow_template, sms_template, data
    )

    if errors:
        return response.validation_failed(errors)

    org, name, description, message = valid_data

    flow_template_dao.update_flow_template_sms_template(
        flow_template, sms_template, description, message, current_user
    )
    res = content_schemas.sms_template_schema.dump(sms_template)
    return response.success(res)


def delete_flow_template_sms_template(flow_template_id, sms_template_id):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    sms_template = flow_template_dao.get_flow_template_sms_template_with_id(
        flow_template, sms_template_id
    )
    if not sms_template:
        return response.not_found()

    flow_template_dao.delete_flow_template_sms_template(sms_template)
    return response.success({})


def get_flow_template_flows(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    template = Template(template_json=flow_template.flow_spec)
    res = flow_template_schemas.flow_schema.dump(template.flows, many=True)
    return response.success(res)


def get_flow_template_flow_details(flow_template_id, flow_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()
    res = flow_template_schemas.flow_details_schema.dump(flow)
    return response.success(res)


def get_flow_template_pages(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    pages = flow_template_dao.get_flow_template_pages(flow_template)
    res = flow_template_schemas.page_schema.dump(pages, many=True)
    return response.success(res)


def get_flow_template_settings(flow_template_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    template = Template(template_json=flow_template.flow_spec)
    if template.start_flow_id:
        template.start_flow = template.get_flow(template.start_flow_id)
    res = flow_template_schemas.flow_template_settings_schema.dump(template)
    return response.success(res)


def update_flow_template_settings(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    try:
        data = flow_template_schemas.update_flow_template_settings_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    start_flow_id = data.get("start_flow_id")
    input_max_tries = data.get("input_max_tries")
    no_input_message_name = data.get("no_input_message_name")
    invalid_input_message_name = data.get("invalid_input_message_name")
    input_tries_exceeded_message_name = data.get("input_tries_exceeded_message_name")

    errors = {}

    template = Template(template_json=flow_template.flow_spec)

    start_flow = template.get_flow(start_flow_id)
    if not start_flow:
        errors["startFlowId"] = ["Invalid Flow Id"]

    message_names = {
        name
        for name in [
            no_input_message_name,
            invalid_input_message_name,
            input_tries_exceeded_message_name,
        ]
        if name
    }
    if message_names:
        messages = flow_template_dao.get_flow_template_messages_with_names(
            flow_template, message_names
        )
        valid_message_names = {message.name for message in messages}

        if no_input_message_name and no_input_message_name not in valid_message_names:
            errors["noInputMessageName"] = [
                f"Invalid message name - {no_input_message_name}"
            ]

        if (
            invalid_input_message_name
            and invalid_input_message_name not in valid_message_names
        ):
            errors["invalidInputMessageName"] = [
                f"Invalid message name - {invalid_input_message_name}"
            ]

        if (
            input_tries_exceeded_message_name
            and input_tries_exceeded_message_name not in valid_message_names
        ):
            errors["inputTriesExceededMessageName"] = [
                f"Invalid message name - {input_tries_exceeded_message_name}"
            ]

    if errors:
        return response.validation_failed(errors)

    flow_template_dao.update_template_settings(
        flow_template,
        template,
        start_flow_id,
        input_max_tries,
        no_input_message_name,
        invalid_input_message_name,
        input_tries_exceeded_message_name,
        current_user,
    )
    return response.success({})


def create_flow_template_flow(flow_template_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    try:
        data = flow_template_schemas.create_flow_schema.load(data)
    except ValidationError as e:
        return response.validation_failed(e.messages)

    name = data.get("name")
    call_max_tries = data.get("call_max_tries")

    errors = {}

    template = Template(template_json=flow_template.flow_spec)

    if any(flow.name.lower() == name.strip().lower() for flow in template.flows):
        errors["name"] = ["A flow with this name already exists in this template"]

    if errors:
        return response.validation_failed(errors)

    flow = flow_template_dao.create_flow(
        flow_template, template, name, call_max_tries, current_user
    )
    res = flow_template_schemas.flow_schema.dump(flow)
    return response.success(res)


def get_flow_template_steps(flow_template_id, flow_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()
    res = []
    for step in flow.steps:
        schema = flow_template_schemas.STEP_SCHEMAS[step.type]
        res.append(schema.dump(step))
    return response.success(res)


def validate_send_email_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_send_email_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    recipient = data.get("recipient")
    email_template_name = data.get("email_template_name")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    email_template = (
        flow_template_dao.get_flow_template_email_template_with_name_and_org_id(
            flow_template, email_template_name, org_id=None
        )
    )
    if not email_template:
        errors["emailTemplateName"] = ["Invalid Email template"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, recipient, email_template_name, next_step_id), errors


def create_send_email_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_send_email_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, recipient, email_template_name, next_step_id = data
    step = flow_template_dao.create_send_email_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        recipient,
        email_template_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_send_email_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_SEND_EMAIL:
        return response.not_found()

    data, errors = validate_send_email_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, recipient, email_template_name, next_step_id = data
    step = flow_template_dao.update_send_email_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        recipient,
        email_template_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_send_sms_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_send_sms_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    recipient = data.get("recipient")
    sms_template_name = data.get("sms_template_name")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    sms_template = (
        flow_template_dao.get_flow_template_sms_template_with_name_and_org_id(
            flow_template, sms_template_name, org_id=None
        )
    )
    if not sms_template:
        errors["smsTemplateName"] = ["Invalid SMS template"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, recipient, sms_template_name, next_step_id), errors


def create_send_sms_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_send_sms_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, recipient, sms_template_name, next_step_id = data
    step = flow_template_dao.create_send_sms_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        recipient,
        sms_template_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_send_sms_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_SEND_SMS:
        return response.not_found()

    data, errors = validate_send_sms_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, recipient, sms_template_name, next_step_id = data
    step = flow_template_dao.update_send_sms_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        recipient,
        sms_template_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_delay_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_delay_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    duration = data.get("duration")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, duration, next_step_id), errors


def create_delay_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_delay_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, duration, next_step_id = data
    step = flow_template_dao.create_delay_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        duration,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_delay_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_DELAY:
        return response.not_found()

    data, errors = validate_delay_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, duration, next_step_id = data
    step = flow_template_dao.update_delay_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        duration,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_questions_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_questions_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    question_set_name = data.get("question_set_name")
    max_questions = data.get("max_questions")
    max_options = data.get("max_options")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    other_questions_steps = template.get_steps_by_type(
        flow_template_constants.STEP_QUESTIONS
    )

    for questions_step in other_questions_steps:
        if step is not None and questions_step.id == step.id:
            continue
        if question_set_name == questions_step.question_set_name:
            errors["questionSetName"] = [
                "A question set with this name already exists in this template"
            ]
            break

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (
        name,
        is_checkpoint,
        question_set_name,
        max_questions,
        max_options,
        next_step_id,
    ), errors


def create_questions_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_questions_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    (
        name,
        is_checkpoint,
        question_set_name,
        max_questions,
        max_options,
        next_step_id,
    ) = data
    step = flow_template_dao.create_questions_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        question_set_name,
        max_questions,
        max_options,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_questions_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_QUESTIONS:
        return response.not_found()

    data, errors = validate_questions_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    (
        name,
        is_checkpoint,
        question_set_name,
        max_questions,
        max_options,
        next_step_id,
    ) = data
    step = flow_template_dao.update_questions_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        question_set_name,
        max_questions,
        max_options,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_play_message_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_play_message_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    message_names = data.get("message_names")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    messages = flow_template_dao.get_flow_template_messages_with_names(
        flow_template, message_names
    )
    if len(messages) != len(message_names):
        valid_message_names = {message.name for message in messages}
        for index, message_name in enumerate(message_names):
            if message_name not in valid_message_names:
                message_name_errors = errors.setdefault("messageNames", {})
                message_name_errors[str(index)] = [
                    "Invalid message name - {}".format(message_name)
                ]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, message_names, next_step_id), errors


def create_play_message_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_play_message_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, message_names, next_step_id = data
    step = flow_template_dao.create_play_message_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        message_names,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_play_message_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_PLAY_MESSAGE:
        return response.not_found()

    data, errors = validate_play_message_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, message_names, next_step_id = data
    step = flow_template_dao.update_play_message_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        message_names,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_get_input_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_get_input_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    purpose = data.get("purpose")
    message_names = data.get("message_names")
    result_name = data.get("result_name")
    result_data_type = data.get("result_data_type")
    options_type = data.get("options_type")
    options = data.get("options")
    dynamic_options_attribute_name = data.get("dynamic_options_attribute_name")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    messages = flow_template_dao.get_flow_template_messages_with_names(
        flow_template, message_names
    )
    if len(messages) != len(message_names):
        valid_message_names = {message.name for message in messages}
        for index, message_name in enumerate(message_names):
            if message_name not in valid_message_names:
                message_name_errors = errors.setdefault("messageNames", {})
                message_name_errors[str(index)] = [
                    "Invalid message name - {}".format(message_name)
                ]

    if purpose == flow_template_constants.GET_INPUT_PURPOSE_MAKE_DECISION:
        if result_name:
            errors["resultName"] = [
                "Result Name must not be provided for making decisions"
            ]
        if result_data_type:
            errors["resultDataType"] = [
                "Result Data Type must not be provided for making decisions"
            ]
        if options_type == flow_template_constants.GET_INPUT_OPTIONS_TYPE_DYNAMIC:
            errors["optionsType"] = [
                "Dynamic options are not supported for making decisions"
            ]
        if dynamic_options_attribute_name:
            errors["dynamicOptionsAttributeName"] = [
                "Attribute not supported for making decisions"
            ]
        if not options:
            errors["message"] = "Options are required"
        if next_step_id:
            errors["nextStepId"] = [
                "Next Step must not be provided for making decisions"
            ]
    elif purpose == flow_template_constants.GET_INPUT_PURPOSE_COLLECT_INFORMATION:
        if not result_name:
            errors["resultName"] = ["Result Name is required"]
        else:
            excluded_step_id = step.id if step else None
            existing_result_names = template.get_result_names(
                excluded_step_id=excluded_step_id
            )
            existing_result_names = {
                name.strip().lower() for name in existing_result_names
            }
            if result_name.strip().lower() in existing_result_names:
                errors["resultName"] = [
                    "A result with this name already exists in this template"
                ]
        if not result_data_type:
            errors["resultDataType"] = ["Result Data Type is required"]
        if options_type == flow_template_constants.GET_INPUT_OPTIONS_TYPE_DYNAMIC:
            if not dynamic_options_attribute_name:
                errors["dynamicOptionsAttributeName"] = ["Attribute is required"]
            if options:
                errors["message"] = "Options must not be provided for dynamic options"
        else:
            if not options:
                errors["message"] = "Options are required"
            if dynamic_options_attribute_name:
                errors["dynamicOptionsAttributeName"] = [
                    "Attribute must not be provided for static options"
                ]
        if next_step_id:
            next_step = flow.get_step(next_step_id)
            if not next_step:
                errors["nextStepId"] = ["Invalid Step"]

    if errors:
        return None, errors

    if options:
        options = [
            (option["key"], option["text"], option["result"], option["next_step_id"])
            for option in options
        ]

    return (
        name,
        is_checkpoint,
        purpose,
        message_names,
        result_name,
        result_data_type,
        options_type,
        options,
        dynamic_options_attribute_name,
        next_step_id,
    ), errors


def create_get_input_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_get_input_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    (
        name,
        is_checkpoint,
        purpose,
        message_names,
        result_name,
        result_data_type,
        options_type,
        options,
        dynamic_options_attribute_name,
        next_step_id,
    ) = data
    step = flow_template_dao.create_get_input_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        purpose,
        message_names,
        result_name,
        result_data_type,
        options_type,
        options,
        dynamic_options_attribute_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_get_input_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_GET_INPUT:
        return response.not_found()

    data, errors = validate_get_input_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    (
        name,
        is_checkpoint,
        purpose,
        message_names,
        result_name,
        result_data_type,
        options_type,
        options,
        dynamic_options_attribute_name,
        next_step_id,
    ) = data
    step = flow_template_dao.update_get_input_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        purpose,
        message_names,
        result_name,
        result_data_type,
        options_type,
        options,
        dynamic_options_attribute_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_record_audio_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_record_audio_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    question_text = data.get("question_text")
    result_name = data.get("result_name")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    excluded_step_id = step.id if step else None
    existing_result_names = template.get_result_names(excluded_step_id=excluded_step_id)
    existing_result_names = {name.strip().lower() for name in existing_result_names}
    if result_name.strip().lower() in existing_result_names:
        errors["resultName"] = [
            "A result with this name already exists in this template"
        ]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, question_text, result_name, next_step_id), errors


def create_record_audio_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_record_audio_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, question_text, result_name, next_step_id = data
    step = flow_template_dao.create_record_audio_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        question_text,
        result_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_record_audio_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_RECORD_AUDIO:
        return response.not_found()

    data, errors = validate_record_audio_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, question_text, result_name, next_step_id = data
    step = flow_template_dao.update_record_audio_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        question_text,
        result_name,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_set_status_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_set_status_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    status_id = data.get("status_id")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    status = flow_template_dao.get_flow_template_status_with_id(
        flow_template, status_id
    )
    if not status:
        errors["statusId"] = ["Invalid Status"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, status, next_step_id), errors


def create_set_status_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_set_status_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, status, next_step_id = data
    step = flow_template_dao.create_set_status_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        status,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_set_status_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_SET_STATUS:
        return response.not_found()

    data, errors = validate_set_status_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, status, next_step_id = data
    step = flow_template_dao.update_set_status_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        status,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_call_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_call_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, next_step_id), errors


def create_call_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_call_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, next_step_id = data
    step = flow_template_dao.create_call_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_call_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_CALL:
        return response.not_found()

    data, errors = validate_call_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, next_step_id = data
    step = flow_template_dao.update_call_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_hang_up_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_hang_up_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    next_step_id = data.get("next_step_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (name, is_checkpoint, next_step_id), errors


def create_hang_up_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_hang_up_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, next_step_id = data
    step = flow_template_dao.create_hang_up_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_hang_up_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_HANG_UP:
        return response.not_found()

    data, errors = validate_hang_up_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, next_step_id = data
    step = flow_template_dao.update_hang_up_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def validate_go_to_flow_step(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.create_update_go_to_flow_step_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    name = data.get("name")
    is_checkpoint = data.get("is_checkpoint")
    go_to_flow_id = data.get("go_to_flow_id")

    errors = {}

    existing_step = flow.get_step_by_name(name, case_insensitive=True)
    if existing_step and (step is None or step.id != existing_step.id):
        errors["name"] = ["A step with this name already exists in this flow"]

    go_to_flow = None
    if go_to_flow_id == flow.id:
        errors["goToFlowId"] = ["Flow Id cannot be the same as the current flow"]
    else:
        go_to_flow = template.get_flow(go_to_flow_id)
        if not go_to_flow:
            errors["goToFlowId"] = ["Invalid Flow"]

    return (name, is_checkpoint, go_to_flow), errors


def create_go_to_flow_step(flow_template_id, flow_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    data, errors = validate_go_to_flow_step(flow_template, template, flow, None, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, go_to_flow = data
    step = flow_template_dao.create_go_to_flow_step(
        flow_template,
        template,
        flow,
        name,
        is_checkpoint,
        go_to_flow,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def update_go_to_flow_step(flow_template_id, flow_id, step_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step or step.type != flow_template_constants.STEP_GO_TO_FLOW:
        return response.not_found()

    data, errors = validate_go_to_flow_step(flow_template, template, flow, step, data)

    if errors:
        return response.validation_failed(errors)

    name, is_checkpoint, go_to_flow = data
    step = flow_template_dao.update_go_to_flow_step(
        flow_template,
        template,
        flow,
        step,
        name,
        is_checkpoint,
        go_to_flow,
        current_user,
    )
    res = flow_template_schemas.step_schema.dump(step)
    return response.success(res)


def get_flow_template_events(flow_template_id, flow_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()
    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()
    res = flow_template_schemas.event_schema.dump(flow.events, many=True)
    return response.success(res)


def validate_event(flow_template, template, flow, step, data):
    try:
        data = flow_template_schemas.update_event_schema.load(data)
    except ValidationError as e:
        return None, e.messages

    next_step_id = data.get("next_step_id")

    errors = {}

    if next_step_id:
        next_step = flow.get_step(next_step_id)
        if not next_step:
            errors["nextStepId"] = ["Invalid Step"]

    return (next_step_id,), errors


def update_event(flow_template_id, flow_id, event_id, data, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)
    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    event = flow.get_event(event_id)
    if not event:
        return response.not_found()

    data, errors = validate_event(flow_template, template, flow, event, data)

    if errors:
        return response.validation_failed(errors)

    (next_step_id,) = data
    step = flow_template_dao.update_event(
        flow_template,
        template,
        flow,
        event,
        next_step_id,
        current_user,
    )
    res = flow_template_schemas.event_schema.dump(step)
    return response.success(res)


def delete_step(flow_template_id, flow_id, step_id, current_user):
    flow_template = flow_template_dao.get_flow_template_with_id(flow_template_id)
    if not flow_template:
        return response.not_found()

    template = Template(template_json=flow_template.flow_spec)

    flow = template.get_flow(flow_id)
    if not flow:
        return response.not_found()

    step = flow.get_step(step_id)
    if not step:
        return response.not_found()

    flow_template_dao.delete_step(
        flow_template,
        template,
        flow,
        step,
        current_user,
    )
    return response.success({})
