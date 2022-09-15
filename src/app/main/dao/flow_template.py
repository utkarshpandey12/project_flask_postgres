import datetime

import shortuuid
from sqlalchemy.orm import contains_eager

from ... import db
from ..models import flow_template as flow_template_constants
from ..models.flow_template import (
    CallStep,
    DelayStep,
    Event,
    Flow,
    GetInputStep,
    GoToFlowStep,
    HangUpStep,
    Option,
    PlayMessageStep,
    QuestionsStep,
    RecordAudioStep,
    SendEmailStep,
    SendSmsStep,
    SetStatusStep,
    Template,
)
from ..models.main import (
    EmailTemplate,
    Field,
    FlowTemplate,
    FlowTemplateField,
    FlowTemplateMessage,
    FlowTemplatePage,
    FlowTemplateStatus,
    SmsTemplate,
)


def get_fields():
    return Field.query.all()


def get_flow_template_with_id(flow_template_id):
    return (
        FlowTemplate.query.join(FlowTemplate.flow_category)
        .options(contains_eager(FlowTemplate.flow_category))
        .filter(FlowTemplate.id == flow_template_id)
        .first()
    )


def get_flow_template_by_name_and_version_identifier(name, version_identifier):
    return FlowTemplate.query.filter(
        db.func.lower(FlowTemplate.name) == name.strip().lower(),
        db.func.lower(FlowTemplate.version_identifier)
        == version_identifier.strip().lower(),
    ).first()


def get_all_flow_templates():
    return (
        FlowTemplate.query.join(FlowTemplate.flow_category)
        .options(contains_eager(FlowTemplate.flow_category))
        .all()
    )


def get_flow_templates_with_ids(flow_template_ids):
    return FlowTemplate.query.filter(FlowTemplate.id.in_(flow_template_ids)).all()


def create_flow_template(
    name, version_identifier, description, flow_category, status, current_user
):
    now = datetime.datetime.now()
    template = Template()
    flow_template = FlowTemplate(
        name=name,
        version_identifier=version_identifier,
        description=description,
        flow_category=flow_category,
        flow_spec=template.to_json(),
        status=status,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(flow_template)
    db.session.flush()
    return flow_template


def set_flow_template_update_audit_fields(flow_template, current_user):
    now = datetime.datetime.now()
    flow_template.updated_by_user = current_user
    flow_template.updated_at = now


def get_field_with_id(field_id):
    return Field.query.get(field_id)


def get_flow_template_field(flow_template, field):
    return FlowTemplateField.query.filter(
        FlowTemplateField.flow_template == flow_template,
        FlowTemplateField.field == field,
    ).first()


def get_flow_template_fields(flow_template, field_type=None):
    query = (
        FlowTemplateField.query.join(FlowTemplateField.field)
        .options(contains_eager(FlowTemplateField.field))
        .filter(
            FlowTemplateField.flow_template == flow_template,
        )
    )

    if field_type:
        query = query.filter(Field.field_type == field_type)

    return query.order_by(FlowTemplateField.sequence).all()


def get_flow_template_field_with_id(flow_template, flow_template_field_id):
    return FlowTemplateField.query.filter(
        FlowTemplateField.flow_template == flow_template,
        FlowTemplateField.id == flow_template_field_id,
    ).first()


def create_flow_template_field(
    flow_template, field, is_mandatory, allow_multiple_values, sequence, current_user
):
    flow_template_field = FlowTemplateField(
        flow_template=flow_template,
        field=field,
        is_mandatory=is_mandatory,
        allow_multiple_values=allow_multiple_values,
        sequence=sequence,
    )
    set_flow_template_update_audit_fields(flow_template, current_user)
    db.session.add(flow_template_field)
    db.session.flush()
    return flow_template_field


def update_flow_template_field(
    flow_template,
    flow_template_field,
    is_mandatory,
    allow_multiple_values,
    sequence,
    current_user,
):
    flow_template_field.is_mandatory = is_mandatory
    flow_template_field.allow_multiple_values = allow_multiple_values
    flow_template_field.sequence = sequence
    set_flow_template_update_audit_fields(flow_template, current_user)
    return flow_template_field


def delete_flow_template_field(flow_template_field):
    db.session.delete(flow_template_field)


def get_flow_template_statuses(flow_template):
    return FlowTemplateStatus.query.filter(
        FlowTemplateStatus.flow_template == flow_template,
    ).all()


def get_flow_template_status_with_id(flow_template, id):
    return FlowTemplateStatus.query.filter(
        FlowTemplateStatus.flow_template == flow_template,
        FlowTemplateStatus.id == id,
    ).first()


def get_flow_template_status_with_name(flow_template, name):
    return FlowTemplateStatus.query.filter(
        FlowTemplateStatus.flow_template == flow_template,
        db.func.lower(FlowTemplateStatus.name) == name.strip().lower(),
    ).first()


def create_flow_template_status(
    flow_template,
    name,
    is_final,
    is_positive,
    is_reattempt_allowed,
    priority,
    sequence,
    current_user,
):
    flow_template_status = FlowTemplateStatus(
        flow_template=flow_template,
        name=name,
        is_final=is_final,
        is_positive=is_positive,
        is_reattempt_allowed=is_reattempt_allowed,
        priority=priority,
        sequence=sequence,
    )
    set_flow_template_update_audit_fields(flow_template, current_user)
    db.session.add(flow_template_status)
    db.session.flush()
    return flow_template_status


def update_flow_template_status(
    flow_template,
    flow_template_status,
    name,
    is_final,
    is_positive,
    is_reattempt_allowed,
    priority,
    sequence,
    current_user,
):

    flow_template_status.name = name
    flow_template_status.is_final = is_final
    flow_template_status.is_positive = is_positive
    flow_template_status.is_reattempt_allowed = is_reattempt_allowed
    flow_template_status.priority = priority
    flow_template_status.sequence = sequence
    set_flow_template_update_audit_fields(flow_template, current_user)
    return flow_template_status


def delete_flow_template_status(flow_template_status):
    db.session.delete(flow_template_status)


def get_flow_template_messages(flow_template, org_id):
    return FlowTemplateMessage.query.filter(
        FlowTemplateMessage.flow_template == flow_template,
        FlowTemplateMessage.org_id == org_id,
    ).all()


def get_flow_template_message_with_name_and_org_id(
    flow_template, name, org_id, case_insensitive=False
):
    query = FlowTemplateMessage.query.filter(
        FlowTemplateMessage.flow_template == flow_template,
        FlowTemplateMessage.org_id == org_id,
    )
    if case_insensitive:
        query = query.filter(
            db.func.lower(FlowTemplateMessage.name) == name.strip().lower()
        )
    else:
        query = query.filter(FlowTemplateMessage.name == name)
    return query.first()


def get_flow_template_messages_with_names(flow_template, names):
    return FlowTemplateMessage.query.filter(
        FlowTemplateMessage.flow_template == flow_template,
        FlowTemplateMessage.name.in_(names),
    ).all()


def get_flow_template_email_templates(flow_template, org_id):
    return EmailTemplate.query.filter(
        EmailTemplate.flow_template == flow_template, EmailTemplate.org_id == org_id
    ).all()


def create_flow_template_message(
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
):
    now = datetime.datetime.now()
    message = FlowTemplateMessage(
        flow_template=flow_template,
        org=org,
        name=name,
        description=description,
        message_type=message_type,
        message_text=message_text,
        attribute=attribute,
        audio_file_path=audio_file_path,
        recording_instruction=recording_instruction,
        sequence=sequence,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    set_flow_template_update_audit_fields(flow_template, current_user)
    db.session.add(message)
    db.session.flush()
    return message


def get_flow_template_email_template_with_name_and_org_id(
    flow_template, name, org_id, case_insensitive=False
):
    query = EmailTemplate.query.filter(
        EmailTemplate.flow_template == flow_template,
        EmailTemplate.org_id == org_id,
    )
    if case_insensitive:
        query = query.filter(db.func.lower(EmailTemplate.name) == name.strip().lower())
    else:
        query = query.filter(EmailTemplate.name == name)
    return query.first()


def get_flow_template_email_template_with_id(flow_template, email_template_id):
    return EmailTemplate.query.filter(
        EmailTemplate.flow_template == flow_template,
        EmailTemplate.id == email_template_id,
    ).first()


def create_flow_template_email_template(
    flow_template,
    org,
    name,
    description,
    email_format,
    subject,
    body_text,
    body_html,
    current_user,
):
    now = datetime.datetime.now()
    email_template = EmailTemplate(
        flow_template=flow_template,
        org=org,
        name=name,
        description=description,
        email_format=email_format,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    set_flow_template_update_audit_fields(flow_template, current_user)
    db.session.add(email_template)
    db.session.flush()
    return email_template


def update_flow_template_email_template(
    flow_template,
    email_template,
    description,
    email_format,
    subject,
    body_text,
    body_html,
    current_user,
):
    email_template.description = description
    email_template.email_format = email_format
    email_template.subject = subject
    email_template.body_text = body_text
    email_template.body_html = body_html
    email_template.updated_at = datetime.datetime.now()
    email_template.updated_by_user = current_user
    set_flow_template_update_audit_fields(flow_template, current_user)


def delete_flow_template_email_template(email_template):
    db.session.delete(email_template)


def get_flow_template_sms_templates(flow_template, org_id):
    return SmsTemplate.query.filter(
        SmsTemplate.flow_template == flow_template, SmsTemplate.org_id == org_id
    ).all()


def get_flow_template_sms_template_with_name_and_org_id(
    flow_template, name, org_id, case_insensitive=False
):
    query = SmsTemplate.query.filter(
        SmsTemplate.flow_template == flow_template,
        SmsTemplate.org_id == org_id,
    )
    if case_insensitive:
        query = query.filter(db.func.lower(SmsTemplate.name) == name.strip().lower())
    else:
        query = query.filter(SmsTemplate.name == name)
    return query.first()


def get_flow_template_sms_template_with_id(flow_template, sms_template_id):
    return SmsTemplate.query.filter(
        SmsTemplate.flow_template == flow_template,
        SmsTemplate.id == sms_template_id,
    ).first()


def create_flow_template_sms_template(
    flow_template,
    org,
    name,
    description,
    message,
    current_user,
):
    now = datetime.datetime.now()
    sms_template = SmsTemplate(
        flow_template=flow_template,
        org=org,
        name=name,
        description=description,
        message=message,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    set_flow_template_update_audit_fields(flow_template, current_user)
    db.session.add(sms_template)
    db.session.flush()
    return sms_template


def update_flow_template_sms_template(
    flow_template,
    sms_template,
    description,
    message,
    current_user,
):
    sms_template.description = description
    sms_template.message = message
    sms_template.updated_at = datetime.datetime.now()
    sms_template.updated_by_user = current_user
    set_flow_template_update_audit_fields(flow_template, current_user)


def delete_flow_template_sms_template(sms_template):
    db.session.delete(sms_template)


def get_flow_template_pages(flow_template):
    return FlowTemplatePage.query.filter(
        FlowTemplatePage.flow_template == flow_template
    ).all()


def update_template_settings(
    flow_template,
    template,
    start_flow_id,
    input_max_tries,
    no_input_message_name,
    invalid_input_message_name,
    input_tries_exceeded_message_name,
    current_user,
):
    template.start_flow_id = start_flow_id
    template.input_max_tries = input_max_tries
    template.no_input_message_name = no_input_message_name
    template.invalid_input_message_name = invalid_input_message_name
    template.input_tries_exceeded_message_name = input_tries_exceeded_message_name
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)


def create_flow(flow_template, template, name, call_max_tries, current_user):
    flow_id = shortuuid.uuid()
    flow = Flow(
        template=template,
        id=flow_id,
        name=name,
        call_max_tries=call_max_tries,
    )
    start_event = Event(
        id=flow_template_constants.EVENT_START,
        name="Start",
        next_step_id=None,
    )
    follow_up_call_never_answered = Event(
        id=flow_template_constants.EVENT_FOLLOW_UP_CALL_NEVER_ANSWERED,
        name="Follow Up Call (Never Answered)",
        next_step_id=None,
    )
    follow_up_call_previously_answered = Event(
        id=flow_template_constants.EVENT_FOLLOW_UP_CALL_PREVIOUSLY_ANSWERED,
        name="Follow Up Call (Previously Answered)",
        next_step_id=None,
    )
    follow_ups_exceeded = Event(
        id=flow_template_constants.EVENT_FOLLOW_UPS_EXCEEDED,
        name="Follow Ups Exceeded",
        next_step_id=None,
    )
    call_input_tries_exceeded = Event(
        id=flow_template_constants.EVENT_CALL_INPUT_TRIES_EXCEEDED,
        name="Call Input Tries Exceeded",
        next_step_id=None,
    )
    flow.add_event(start_event)
    flow.add_event(follow_up_call_never_answered)
    flow.add_event(follow_up_call_previously_answered)
    flow.add_event(follow_ups_exceeded)
    flow.add_event(call_input_tries_exceeded)
    template.add_flow(flow)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return flow


def create_send_email_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    recipient,
    email_template_name,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = SendEmailStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        recipient=recipient,
        email_template_name=email_template_name,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_send_email_step(
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
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.recipient = recipient
    step.email_template_name = email_template_name
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_send_sms_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    recipient,
    sms_template_name,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = SendSmsStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        recipient=recipient,
        sms_template_name=sms_template_name,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_send_sms_step(
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
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.recipient = recipient
    step.sms_template_name = sms_template_name
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_delay_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    duration,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = DelayStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        duration=duration,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_delay_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    duration,
    next_step_id,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.duration = duration
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_questions_step(
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
):
    step_id = shortuuid.uuid()
    step = QuestionsStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        question_set_name=question_set_name,
        max_questions=max_questions,
        max_options=max_options,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_questions_step(
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
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.question_set_name = question_set_name
    step.max_questions = max_questions
    step.max_options = max_options
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_play_message_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    message_names,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = PlayMessageStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        message_names=message_names,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_play_message_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    message_names,
    next_step_id,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.message_names = message_names
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_get_input_step(
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
):
    step_id = shortuuid.uuid()
    option_objs = None
    if options:
        option_objs = [
            Option(key=key, text=text, result=result, next_step_id=next_step_id)
            for (key, text, result, next_step_id) in options
        ]
    step = GetInputStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        purpose=purpose,
        message_names=message_names,
        result_name=result_name,
        result_data_type=result_data_type,
        options_type=options_type,
        options=option_objs,
        dynamic_options_attribute_name=dynamic_options_attribute_name,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_get_input_step(
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
):
    option_objs = None
    if options:
        option_objs = [
            Option(key=key, text=text, result=result, next_step_id=next_step_id)
            for (key, text, result, next_step_id) in options
        ]
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.purpose = purpose
    step.message_names = message_names
    step.result_name = result_name
    step.result_data_type = result_data_type
    step.options_type = options_type
    step.options = option_objs
    step.dynamic_options_attribute_name = dynamic_options_attribute_name
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_record_audio_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    question_text,
    result_name,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = RecordAudioStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        question_text=question_text,
        result_name=result_name,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_record_audio_step(
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
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.question_text = question_text
    step.result_name = result_name
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_set_status_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    status,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = SetStatusStep(
        id=step_id,
        flow=flow,
        name=name,
        status_id=status.id,
        is_checkpoint=is_checkpoint,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_set_status_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    status,
    next_step_id,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.status_id = status.id
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_call_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = CallStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_call_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    next_step_id,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_hang_up_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    next_step_id,
    current_user,
):
    step_id = shortuuid.uuid()
    step = HangUpStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        next_step_id=next_step_id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_hang_up_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    next_step_id,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def create_go_to_flow_step(
    flow_template,
    template,
    flow,
    name,
    is_checkpoint,
    go_to_flow,
    current_user,
):
    step_id = shortuuid.uuid()
    step = GoToFlowStep(
        id=step_id,
        flow=flow,
        name=name,
        is_checkpoint=is_checkpoint,
        go_to_flow_id=go_to_flow.id,
    )
    flow.add_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_go_to_flow_step(
    flow_template,
    template,
    flow,
    step,
    name,
    is_checkpoint,
    go_to_flow,
    current_user,
):
    step.name = name
    step.is_checkpoint = is_checkpoint
    step.go_to_flow_id = go_to_flow.id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return step


def update_event(
    flow_template,
    template,
    flow,
    event,
    next_step_id,
    current_user,
):
    event.next_step_id = next_step_id
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
    return event


def delete_step(
    flow_template,
    template,
    flow,
    step,
    current_user,
):
    flow.delete_step(step)
    flow_template.flow_spec = template.to_json()
    set_flow_template_update_audit_fields(flow_template, current_user)
