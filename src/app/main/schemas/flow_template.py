from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf, Range

from ..models import flow_template as flow_template_constants
from ..models import main as constants
from .flow_category import FlowCategorySchema


class FlowTemplateSchema(Schema):
    id = fields.Integer(
        strict=True,
        required=True,
        error_messages={
            "required": "Id is required",
            "null": "Id is required",
            "invalid": "Id must be a valid number",
        },
    )
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    version_identifier = fields.String(
        data_key="versionIdentifier",
        required=True,
        validate=[
            Length(
                min=1,
                max=30,
                error="Version Identifier must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "required": "Version Identifier is required",
            "null": "Version Identifier is required",
            "invalid": "Version Identifier must be a string",
        },
    )
    description = fields.String(allow_none=True)
    flow_category_id = fields.Integer(
        data_key="flowCategoryId",
        required=True,
        error_messages={
            "required": "Flow Category Id is required",
            "null": "Flow Category Id is required",
            "invalid": "Flow Category Id must be an integer",
        },
    )
    flow_category = fields.Nested(FlowCategorySchema, data_key="flowCategory")
    status = fields.String()


flow_template_schema = FlowTemplateSchema(
    only=(
        "id",
        "name",
        "version_identifier",
        "description",
        "flow_category.id",
        "flow_category.name",
        "status",
    ),
)

create_flow_template_schema = FlowTemplateSchema(
    only=("name", "version_identifier", "description", "flow_category_id"),
)


class FlowTemplateSettings(Schema):
    start_flow_id = fields.String(
        data_key="startFlowId",
        required=True,
        allow_none=True,
        error_messages={
            "invalid": "Start Flow Id must be a string",
        },
    )
    start_flow = fields.Nested("FlowSchema", data_key="startFlow")
    input_max_tries = fields.Integer(
        data_key="inputMaxTries",
        required=True,
        allow_none=True,
        error_messages={
            "invalid": "Input Max Tries must be an integer",
        },
    )
    no_input_message_name = fields.String(
        data_key="noInputMessageName",
        required=True,
        allow_none=True,
        error_messages={
            "invalid": "No Input Message must be a string",
        },
    )
    invalid_input_message_name = fields.String(
        data_key="invalidInputMessageName",
        required=True,
        allow_none=True,
        error_messages={
            "invalid": "Invalid Input Message must be a string",
        },
    )
    input_tries_exceeded_message_name = fields.String(
        data_key="inputTriesExceededMessageName",
        required=True,
        allow_none=True,
        error_messages={
            "invalid": "Input Tries Exceeded Message must be a string",
        },
    )


update_flow_template_settings_schema = FlowTemplateSettings(
    only=(
        "start_flow_id",
        "input_max_tries",
        "no_input_message_name",
        "invalid_input_message_name",
        "input_tries_exceeded_message_name",
    )
)

flow_template_settings_schema = FlowTemplateSettings(
    only=(
        "start_flow.id",
        "start_flow.name",
        "input_max_tries",
        "no_input_message_name",
        "invalid_input_message_name",
        "input_tries_exceeded_message_name",
    )
)


class FlowSchema(Schema):
    id = fields.String()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    call_max_tries = fields.Integer(
        data_key="callMaxTries",
        required=True,
        error_messages={
            "required": "Call Max Tries is required",
            "null": "Call Max Tries is required",
            "invalid": "Call Max Tries must be an integer",
        },
    )


flow_schema = FlowSchema(only=("id", "name", "call_max_tries"))

flow_details_schema = FlowSchema(only=("id", "name", "call_max_tries"))

create_flow_schema = FlowSchema(only=("name", "call_max_tries"))


class PageSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    flow = fields.Nested("FlowSchema")


page_schema = PageSchema(only=("id", "name", "flow.id", "flow.name"))


class StepSchema(Schema):
    id = fields.String()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    type = fields.String()
    is_checkpoint = fields.Boolean(data_key="isCheckpoint")
    transitions = fields.Nested("TransitionSchema", many=True)
    next_step_id = fields.String(data_key="nextStepId", required=True, allow_none=True)


step_schema = StepSchema(only=("id", "name", "type"))


class TransitionSchema(Schema):
    name = fields.String()
    destination = fields.String()


class SendEmailStepSchema(StepSchema):
    recipient = fields.String(
        required=True,
        validate=OneOf(
            [
                flow_template_constants.RECIPIENT_CANDIDATE,
                flow_template_constants.RECIPIENT_CAMPAIGN_OWNER,
                flow_template_constants.RECIPIENT_SYS_ADMIN,
            ],
            error="Recipient must be one of - {choices}.",
        ),
    )
    email_template_name = fields.String(data_key="emailTemplateName", required=True)


send_email_step_schema = SendEmailStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "recipient",
        "email_template_name",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_send_email_step_schema = SendEmailStepSchema(
    only=("name", "is_checkpoint", "recipient", "email_template_name", "next_step_id")
)


class SendSmsStepSchema(StepSchema):
    recipient = fields.String(
        required=True,
        validate=OneOf(
            [
                flow_template_constants.RECIPIENT_CANDIDATE,
                flow_template_constants.RECIPIENT_CAMPAIGN_OWNER,
                flow_template_constants.RECIPIENT_SYS_ADMIN,
            ],
            error="Recipient must be one of - {choices}.",
        ),
    )
    sms_template_name = fields.String(data_key="smsTemplateName", required=True)


send_sms_step_schema = SendSmsStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "recipient",
        "next_step_id",
        "sms_template_name",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_send_sms_step_schema = SendSmsStepSchema(
    only=("name", "is_checkpoint", "recipient", "sms_template_name", "next_step_id")
)


class DelayStepSchema(StepSchema):
    duration = fields.Integer(
        required=True,
        strict=True,
        error_messages={
            "required": "Duration is required",
            "null": "Duration is required",
            "invalid": "Duration must be a valid number",
        },
    )


delay_step_schema = DelayStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "duration",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_delay_step_schema = DelayStepSchema(
    only=("name", "is_checkpoint", "duration", "next_step_id")
)


class QuestionsStepSchema(StepSchema):
    question_set_name = fields.String(
        data_key="questionSetName",
        required=True,
        validate=[
            Length(
                min=1,
                max=100,
                error="Question Set Name must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "required": "Question Set Name is required",
            "null": "Question Set Name is required",
            "invalid": "Question Set Name must be a string",
        },
    )
    max_questions = fields.Integer(
        data_key="maxQuestions",
        required=True,
        strict=True,
        error_messages={
            "required": "Max Questions is required",
            "null": "Max Questions is required",
            "invalid": "Max Questions must be a valid number",
        },
    )
    max_options = fields.Integer(
        data_key="maxOptions",
        required=True,
        strict=True,
        error_messages={
            "required": "Max Options is required",
            "null": "Max Options is required",
            "invalid": "Max Options must be a valid number",
        },
    )


questions_step_schema = QuestionsStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "question_set_name",
        "max_questions",
        "max_options",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_questions_step_schema = QuestionsStepSchema(
    only=(
        "name",
        "is_checkpoint",
        "question_set_name",
        "max_questions",
        "max_options",
        "next_step_id",
    )
)


class PlayMessageStepSchema(StepSchema):
    message_names = fields.List(
        fields.String(),
        data_key="messageNames",
        required=True,
        validate=[
            Length(
                min=1,
                error="One or more messages are required",
            ),
        ],
        error_messages={
            "required": "One or more messages are required",
            "null": "One or more messages are required",
            "invalid": "Messages must be an array",
        },
    )


play_message_step_schema = PlayMessageStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "message_names",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_play_message_step_schema = PlayMessageStepSchema(
    only=("name", "is_checkpoint", "message_names", "next_step_id")
)


class OptionSchema(Schema):
    key = fields.Integer(
        required=True,
        strict=True,
        validate=Range(min=0, max=9, error="Key must be a number between 0 and 9"),
        error_messages={
            "required": "Key is required",
            "null": "Key is required",
            "invalid": "Key must be a valid number",
        },
    )
    text = fields.String(
        allow_none=True,
        validate=[
            Length(
                min=1,
                max=100,
                error="Text must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "invalid": "Text must be a string",
        },
    )
    result = fields.String(
        allow_none=True,
        validate=[
            Length(
                min=1,
                max=100,
                error="Result must be between {min} and {max} characters",
            ),
        ],
        error_messages={
            "invalid": "Result must be a string",
        },
    )
    next_step_id = fields.String(data_key="nextStepId", required=True, allow_none=True)


class GetInputStepSchema(StepSchema):
    purpose = fields.String(
        required=True,
        validate=OneOf(
            [
                flow_template_constants.GET_INPUT_PURPOSE_MAKE_DECISION,
                flow_template_constants.GET_INPUT_PURPOSE_COLLECT_INFORMATION,
            ],
            error="Purpose must be one of - {choices}.",
        ),
    )
    message_names = fields.List(
        fields.String(),
        data_key="messageNames",
        required=True,
        validate=[
            Length(
                min=1,
                error="One or more messages are required",
            ),
        ],
        error_messages={
            "required": "One or more messages are required",
            "null": "One or more messages are required",
            "invalid": "Messages must be an array",
        },
    )
    result_name = fields.String(
        data_key="resultName",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Result Name is required",
            "invalid": "Result Name must be a valid string",
        },
    )
    result_data_type = fields.String(
        data_key="resultDataType",
        required=True,
        allow_none=True,
        validate=OneOf(
            [
                flow_template_constants.GET_INPUT_RESULT_DATA_TYPE_TEXT,
                flow_template_constants.GET_INPUT_RESULT_DATA_TYPE_INTEGER,
                flow_template_constants.GET_INPUT_RESULT_DATA_TYPE_DATE,
                flow_template_constants.GET_INPUT_RESULT_DATA_TYPE_TIME,
            ],
            error="Result Data Type must be one of - {choices}.",
        ),
        error_messages={
            "required": "Result Data Type is required",
        },
    )
    options_type = fields.String(
        data_key="optionsType",
        required=True,
        validate=OneOf(
            [
                flow_template_constants.GET_INPUT_OPTIONS_TYPE_STATIC,
                flow_template_constants.GET_INPUT_OPTIONS_TYPE_DYNAMIC,
            ],
            error="Options Type must be one of - {choices}.",
        ),
    )
    options = fields.Nested("OptionSchema", many=True, required=True, allow_none=True)
    dynamic_options_attribute_name = fields.String(
        data_key="dynamicOptionsAttributeName", required=True, allow_none=True
    )


get_input_step_schema = GetInputStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "purpose",
        "message_names",
        "result_name",
        "result_data_type",
        "options_type",
        "options.key",
        "options.text",
        "options.result",
        "options.next_step_id",
        "dynamic_options_attribute_name",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_get_input_step_schema = GetInputStepSchema(
    only=(
        "name",
        "is_checkpoint",
        "purpose",
        "message_names",
        "result_name",
        "result_data_type",
        "options_type",
        "options",
        "options.key",
        "options.text",
        "options.result",
        "options.next_step_id",
        "dynamic_options_attribute_name",
        "next_step_id",
    )
)


class RecordAudioStepSchema(StepSchema):
    question_text = fields.String(
        data_key="questionText",
        required=True,
        error_messages={
            "required": "Question text is required",
            "null": "Question text is required",
            "invalid": "Question text must be a valid string",
        },
    )
    result_name = fields.String(
        data_key="resultName",
        required=True,
        error_messages={
            "required": "Result Name is required",
            "null": "Result Name is required",
            "invalid": "Result Name must be a valid string",
        },
    )


record_audio_step_schema = RecordAudioStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "question_text",
        "result_name",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_record_audio_step_schema = RecordAudioStepSchema(
    only=("name", "is_checkpoint", "question_text", "result_name", "next_step_id")
)


class SetStatusStepSchema(StepSchema):
    status_id = fields.Integer(
        data_key="statusId",
        strict=True,
        required=True,
        error_messages={
            "required": "Status Id is required",
            "null": "Status Id is is required",
            "invalid": "Status Id must be a valid number",
        },
    )


set_status_step_schema = SetStatusStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "status_id",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_set_status_step_schema = SetStatusStepSchema(
    only=("name", "is_checkpoint", "status_id", "next_step_id")
)


class CallStepSchema(StepSchema):
    pass


call_step_schema = CallStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_call_step_schema = CallStepSchema(
    only=("name", "is_checkpoint", "next_step_id")
)


class HangUpStepSchema(StepSchema):
    pass


hang_up_step_schema = HangUpStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "next_step_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_hang_up_step_schema = HangUpStepSchema(
    only=("name", "is_checkpoint", "next_step_id")
)


class GoToFlowStepSchema(StepSchema):
    go_to_flow_id = fields.String(
        data_key="goToFlowId", required=True, allow_none=False
    )


go_to_flow_step_schema = GoToFlowStepSchema(
    only=(
        "id",
        "name",
        "type",
        "is_checkpoint",
        "go_to_flow_id",
        "transitions.name",
        "transitions.destination",
    )
)

create_update_go_to_flow_step_schema = GoToFlowStepSchema(
    only=("name", "is_checkpoint", "go_to_flow_id")
)


STEP_SCHEMAS = {
    flow_template_constants.STEP_SEND_EMAIL: send_email_step_schema,
    flow_template_constants.STEP_SEND_SMS: send_sms_step_schema,
    flow_template_constants.STEP_DELAY: delay_step_schema,
    flow_template_constants.STEP_QUESTIONS: questions_step_schema,
    flow_template_constants.STEP_PLAY_MESSAGE: play_message_step_schema,
    flow_template_constants.STEP_GET_INPUT: get_input_step_schema,
    flow_template_constants.STEP_RECORD_AUDIO: record_audio_step_schema,
    flow_template_constants.STEP_SET_STATUS: set_status_step_schema,
    flow_template_constants.STEP_CALL: call_step_schema,
    flow_template_constants.STEP_HANG_UP: hang_up_step_schema,
    flow_template_constants.STEP_GO_TO_FLOW: go_to_flow_step_schema,
}


class FieldSchema(Schema):
    id = fields.Integer()
    name = fields.String()


field_schema = FieldSchema(only=("id", "name"))


class DynamicAttributeSchema(Schema):
    id = fields.String()
    name = fields.String()


dynamic_attribute_schema = DynamicAttributeSchema(only=("id", "name"))


class EventSchema(Schema):
    id = fields.String()
    name = fields.String()
    next_step_id = fields.String(data_key="nextStepId")


event_schema = EventSchema(only=("id", "name", "next_step_id"))

update_event_schema = EventSchema(only=("next_step_id",))


class FlowTemplateFieldSchema(Schema):
    id = fields.String()
    field_id = fields.Integer(
        data_key="fieldId",
        required=True,
        error_messages={
            "required": "Field Id is required",
            "null": "Field Id is required",
            "invalid": "Field Id must be an integer",
        },
    )
    field = fields.Nested(FieldSchema)
    is_mandatory = fields.Boolean(
        data_key="isMandatory",
        required=True,
        error_messages={
            "required": "isMandatory is required",
            "null": "isMandatory is required",
            "invalid": "isMandatory must be a boolean",
        },
    )
    allow_multiple_values = fields.Boolean(data_key="allowMultipleValues")
    sequence = fields.Integer(
        required=True,
        error_messages={
            "required": "Sequence is required",
            "null": "Sequence is required",
            "invalid": "Sequence must be an integer",
        },
    )


create_flow_template_field_schema = FlowTemplateFieldSchema(
    only=("field_id", "is_mandatory", "allow_multiple_values", "sequence")
)

update_flow_template_field_schema = FlowTemplateFieldSchema(
    only=("is_mandatory", "allow_multiple_values", "sequence")
)


flow_template_field_schema = FlowTemplateFieldSchema(
    only=(
        "id",
        "field.id",
        "field.name",
        "is_mandatory",
        "allow_multiple_values",
        "sequence",
    )
)


class FlowTemplateStatusSchema(Schema):
    id = fields.Integer()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    is_final = fields.Boolean(
        data_key="isFinal",
        required=True,
        error_messages={
            "required": "isFinal is required",
            "null": "isFinal is required",
            "invalid": "isFinal must be a boolean",
        },
    )
    is_positive = fields.Boolean(
        data_key="isPositive",
        required=True,
        error_messages={
            "required": "isPositive is required",
            "null": "isPositive is required",
            "invalid": "isPositive must be a boolean",
        },
    )
    is_reattempt_allowed = fields.Boolean(
        data_key="isReattemptAllowed",
        required=True,
        error_messages={
            "required": "isReattemptAllowed is required",
            "null": "isReattemptAllowed is required",
            "invalid": "isReattemptAllowed must be a boolean",
        },
    )
    priority = fields.Integer(
        required=True,
        error_messages={
            "required": "Priority is required",
            "null": "Priority is required",
            "invalid": "Priority must be an integer",
        },
    )
    sequence = fields.Integer(
        required=True,
        error_messages={
            "required": "Sequence is required",
            "null": "Sequence is required",
            "invalid": "Sequence must be an integer",
        },
    )


flow_template_status_schema = FlowTemplateStatusSchema(
    only=(
        "id",
        "name",
        "is_final",
        "is_positive",
        "is_reattempt_allowed",
        "priority",
        "sequence",
    )
)


create_update_flow_template_status_schema = FlowTemplateStatusSchema(
    only=(
        "name",
        "is_final",
        "is_positive",
        "is_reattempt_allowed",
        "priority",
        "sequence",
    )
)


class FlowTemplateMessageSchema(Schema):
    id = fields.Integer()
    org_id = fields.Integer(
        data_key="orgId",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Org Id is required",
            "invalid": "A valid Org Id is required",
        },
    )
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    description = fields.String(required=True, allow_none=True)
    message_type = fields.String(
        data_key="messageType",
        required=True,
        validate=OneOf(
            [
                constants.MESSAGE_TYPE_AUDIO_FROM_TEMPLATE,
                constants.MESSAGE_TYPE_AUDIO_FROM_CAMPAIGN,
                constants.MESSAGE_TYPE_TEXT_TO_SPEECH_STATIC,
                constants.MESSAGE_TYPE_TEXT_TO_SPEECH_DYNAMIC,
            ],
            error="Message Type must be one of - {choices}.",
        ),
    )
    message_text = fields.String(data_key="messageText", required=True, allow_none=True)
    audio_file_url = fields.String(data_key="audioFileUrl")
    attribute = fields.String(data_key="attribute", required=True, allow_none=True)
    recording_instruction_id = fields.Integer(
        data_key="recordingInstructionId",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Recording Instruction Id is required",
            "invalid": "A valid Recording Instruction Id is required",
        },
    )
    sequence = fields.Integer(
        data_key="sequence",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Sequence is required",
            "invalid": "A valid Sequence is required",
        },
    )


flow_template_message_schema = FlowTemplateMessageSchema(
    only=(
        "id",
        "name",
        "description",
        "message_type",
        "message_text",
        "attribute",
        "audio_file_url",
        "sequence",
    )
)


create_flow_template_message_schema = FlowTemplateMessageSchema(
    only=(
        "org_id",
        "name",
        "description",
        "message_type",
        "message_text",
        "attribute",
        "recording_instruction_id",
        "sequence",
    )
)
