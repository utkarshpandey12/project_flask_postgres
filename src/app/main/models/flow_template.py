TRANSITION_NEXT = "next"


class Transition:
    def __init__(self, *, transition_json=None, name=None, destination=None):
        if transition_json:
            self.name = transition_json["name"]
            self.destination = transition_json.get("destination")
        else:
            self.name = name
            self.destination = destination

    def to_json(self):
        return {"name": self.name, "destination": self.destination}


class Event:
    def __init__(self, *, event_json=None, id=None, name=None, next_step_id=None):
        if event_json:
            self.id = event_json["id"]
            self.name = event_json["name"]
            self.next_step_id = event_json.get("nextStepId")
        else:
            self.id = id
            self.name = name
            self.next_step_id = next_step_id

    def delete_references_to_step(self, deleted_step_id):
        if self.next_step_id == deleted_step_id:
            self.next_step_id = None

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "nextStepId": self.next_step_id,
        }


class Condition:
    def __init__(
        self, *, condition_json=None, attribute=None, value=None, else_transition=None
    ):
        if condition_json:
            self.attribute = condition_json["attribute"]
            self.value = condition_json["value"]
            self.else_transition = condition_json["else"]
        else:
            self.attribute = attribute
            self.value = value
            self.else_transition = else_transition

    def to_json(self):
        return {
            "attribute": self.attribute,
            "value": self.value,
            "else": self.else_transition,
        }


class Option:
    def __init__(
        self, *, option_json=None, key=None, text=None, result=None, next_step_id=None
    ):
        if option_json:
            self.key = option_json["key"]
            self.text = option_json.get("text")
            self.result = option_json.get("result")
            self.next_step_id = option_json.get("nextStepId")
        else:
            self.key = key
            self.text = text
            self.result = result
            self.next_step_id = next_step_id

    def to_json(self):
        option = {
            "key": self.key,
        }
        if self.text:
            option["text"] = self.text
        if self.result:
            option["result"] = self.result
        if self.next_step_id:
            option["nextStepId"] = self.next_step_id
        return option


STEP_SEND_EMAIL = "SendEmail"
STEP_SEND_SMS = "SendSms"
STEP_DELAY = "Delay"
STEP_PLAY_MESSAGE = "PlayMessage"
STEP_QUESTIONS = "Questions"
STEP_GET_INPUT = "GetInput"
STEP_RECORD_AUDIO = "RecordAudio"
STEP_SET_STATUS = "SetStatus"
STEP_CALL = "Call"
STEP_HANG_UP = "HangUp"
STEP_RESUME_FROM_CHECKPOINT = "ResumeFromCheckpoint"
STEP_GO_TO_FLOW = "GoToFlow"


class Step:
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        type=None,
        is_checkpoint=None,
        next_step_id=None,
    ):
        self.flow = flow
        if step_json:
            self.id = step_json["id"]
            self.name = step_json["name"]
            self.type = step_json.get("type")
            self.is_checkpoint = step_json.get("isCheckpoint", False)
            self.next_step_id = step_json.get("nextStepId")
            self.condition = None
            if "condition" in step_json:
                self.condition = Condition(condition_json=step_json["condition"])
        else:
            self.id = id
            self.name = name
            self.type = type
            self.is_checkpoint = is_checkpoint
            self.next_step_id = next_step_id
            self.condition = None

        self.next_step_ids = {}
        self.transitions = []

        if self.next_step_id:
            self.add_next_step_id(TRANSITION_NEXT, self.next_step_id)
            self.add_transition(TRANSITION_NEXT, self.next_step_id)

    def get_next_step_id(self, value):
        return self.next_step_ids.get(value)

    def add_next_step_id(self, value, next_step_id):
        self.next_step_ids[value] = next_step_id

    def delete_next_step_id(self, value):
        if value in self.next_step_ids:
            del self.next_step_ids[value]

    def add_transition(self, name, destination):
        transition = Transition(name=name, destination=destination)
        self.transitions.append(transition)

    def delete_transition(self, destination):
        self.transitions = [
            transition
            for transition in self.transitions
            if transition.destination != destination
        ]

    def delete_references_to_step(self, deleted_step_id):
        if self.next_step_id == deleted_step_id:
            self.next_step_id = None
            self.delete_next_step_id(TRANSITION_NEXT)
            self.delete_transition(deleted_step_id)

    def to_json(self):
        step_json = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }
        if self.is_checkpoint:
            step_json["isCheckpoint"] = self.is_checkpoint
        if self.condition:
            step_json["condition"] = self.condition.to_json()
        if self.next_step_id:
            step_json["nextStepId"] = self.next_step_id
        return step_json


RECIPIENT_CANDIDATE = "Candidate"
RECIPIENT_CAMPAIGN_OWNER = "Campaign Owner"
RECIPIENT_SYS_ADMIN = "System Administrator"


class SendSmsStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        recipient=None,
        sms_template_name=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_SEND_SMS,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.recipient = step_json["recipient"]
            self.sms_template_name = step_json["smsTemplateName"]
        else:
            self.recipient = recipient
            self.sms_template_name = sms_template_name

    def to_json(self):
        step_json = super().to_json()
        step_json["recipient"] = self.recipient
        step_json["smsTemplateName"] = self.sms_template_name
        return step_json


class SendEmailStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        recipient=None,
        email_template_name=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_SEND_EMAIL,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.recipient = step_json["recipient"]
            self.email_template_name = step_json["emailTemplateName"]
        else:
            self.recipient = recipient
            self.email_template_name = email_template_name

    def to_json(self):
        step_json = super().to_json()
        step_json["recipient"] = self.recipient
        step_json["emailTemplateName"] = self.email_template_name
        return step_json


class DelayStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        duration=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_DELAY,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.duration = step_json["duration"]
        else:
            self.duration = duration

    def to_json(self):
        step_json = super().to_json()
        step_json["duration"] = self.duration
        return step_json


class CallStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_CALL,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )


class HangUpStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_HANG_UP,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )


class QuestionsStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        question_set_name=None,
        max_questions=None,
        max_options=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_QUESTIONS,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.question_set_name = step_json["questionSetName"]
            self.max_questions = step_json["maxQuestions"]
            self.max_options = step_json["maxOptions"]
        else:
            self.question_set_name = question_set_name
            self.max_questions = max_questions
            self.max_options = max_options

    def to_json(self):
        step_json = super().to_json()
        step_json["questionSetName"] = self.question_set_name
        step_json["maxQuestions"] = self.max_questions
        step_json["maxOptions"] = self.max_options
        return step_json


class PlayMessageStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        message_names=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_PLAY_MESSAGE,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.message_names = step_json["messageNames"]
        else:
            self.message_names = message_names

    def to_json(self):
        step_json = super().to_json()
        step_json["messageNames"] = self.message_names
        return step_json


DYNAMIC_ATTRIBUTE_TYPE_CAMPAIGN_FIELD = "campaign-field"

DYNAMIC_ATTRIBUTE_DATA_TYPE_DATE = "date"
DYNAMIC_ATTRIBUTE_DATA_TYPE_TIME = "time"

GET_INPUT_PURPOSE_MAKE_DECISION = "Make Decision"
GET_INPUT_PURPOSE_COLLECT_INFORMATION = "Collect Information"

GET_INPUT_RESULT_DATA_TYPE_TEXT = "TE"
GET_INPUT_RESULT_DATA_TYPE_INTEGER = "IN"
GET_INPUT_RESULT_DATA_TYPE_DATE = "DA"
GET_INPUT_RESULT_DATA_TYPE_TIME = "TI"

GET_INPUT_OPTIONS_TYPE_STATIC = "Static"
GET_INPUT_OPTIONS_TYPE_DYNAMIC = "Dynamic"


class GetInputStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        purpose=None,
        message_names=None,
        result_name=None,
        result_data_type=None,
        options_type=None,
        options=None,
        dynamic_options_attribute_name=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_GET_INPUT,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.purpose = step_json["purpose"]
            self.message_names = step_json["messageNames"]
            self.result_name = step_json.get("resultName")
            self.result_data_type = step_json.get("resultDataType")
            self.options_type = step_json["optionsType"]

            self.options = None
            if "options" in step_json:
                self.options = []
                for option_json in step_json["options"]:
                    option = Option(option_json=option_json)
                    self.options.append(option)

            self.dynamic_options_attribute_name = None
            if "dynamicOptionsAttributeName" in step_json:
                self.dynamic_options_attribute_name = step_json[
                    "dynamicOptionsAttributeName"
                ]
        else:
            self.purpose = purpose
            self.message_names = message_names
            self.result_name = result_name
            self.result_data_type = result_data_type
            self.options_type = options_type
            self.options = options
            self.dynamic_options_attribute_name = dynamic_options_attribute_name

        if self.purpose == GET_INPUT_PURPOSE_MAKE_DECISION:
            for option in self.options:
                self.add_next_step_id(option.key, option.next_step_id)
                if option.text:
                    self.add_next_step_id(option.text.lower(), option.next_step_id)
                transition_name = (
                    f"{option.key} - {option.text}" if option.text else str(option.key)
                )
                self.add_transition(transition_name, option.next_step_id)

    def delete_references_to_step(self, deleted_step_id):
        super().delete_references_to_step(deleted_step_id)
        for option in self.options:
            if option.next_step_id == deleted_step_id:
                option.next_step_id = None
                self.delete_next_step_id(option.key)
                if option.text:
                    self.delete_next_step_id(option.text.lower())
                self.delete_transition(deleted_step_id)

    def get_option_by_key(self, key):
        if self.options:
            for option in self.options:
                if option.key == key:
                    return option
        return None

    def get_option_by_text(self, text):
        if self.options:
            for option in self.options:
                if option.text.lower() == text.lower():
                    return option
        return None

    def get_option_by_key_or_text(self, key, text):
        option = None
        if key is not None:
            option = self.get_option_by_key(key)
        elif text:
            option = self.get_option_by_text(text)
        return option

    def to_json(self):
        step_json = super().to_json()
        step_json["purpose"] = self.purpose
        step_json["messageNames"] = self.message_names
        step_json["resultName"] = self.result_name
        step_json["resultDataType"] = self.result_data_type
        step_json["optionsType"] = self.options_type
        if self.options:
            step_json["options"] = [option.to_json() for option in self.options]
        if self.dynamic_options_attribute_name:
            step_json[
                "dynamicOptionsAttributeName"
            ] = self.dynamic_options_attribute_name
        return step_json


class RecordAudioStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        question_text=None,
        result_name=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_RECORD_AUDIO,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.question_text = step_json.get("questionText")
            self.result_name = step_json.get("resultName")
        else:
            self.question_text = question_text
            self.result_name = result_name

    def to_json(self):
        step_json = super().to_json()
        step_json["questionText"] = self.question_text
        step_json["resultName"] = self.result_name
        return step_json


class SetStatusStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        status_id=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_SET_STATUS,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )
        if step_json:
            self.status_id = step_json["statusId"]
        else:
            self.status_id = status_id

    def to_json(self):
        step_json = super().to_json()
        step_json["statusId"] = self.status_id
        return step_json


class ResumeFromCheckpointStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        next_step_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_RESUME_FROM_CHECKPOINT,
            is_checkpoint=is_checkpoint,
            next_step_id=next_step_id,
        )


class GoToFlowStep(Step):
    def __init__(
        self,
        *,
        flow=None,
        step_json=None,
        id=None,
        name=None,
        is_checkpoint=None,
        go_to_flow_id=None,
    ):
        super().__init__(
            flow=flow,
            step_json=step_json,
            id=id,
            name=name,
            type=STEP_GO_TO_FLOW,
            is_checkpoint=is_checkpoint,
            next_step_id=None,
        )
        if step_json:
            self.go_to_flow_id = step_json["goToFlowId"]
        else:
            self.go_to_flow_id = go_to_flow_id

    def to_json(self):
        step_json = super().to_json()
        step_json["goToFlowId"] = self.go_to_flow_id
        return step_json


EVENT_START = "start"
EVENT_CONTINUE = "continue"
EVENT_CALL_NOT_CONNECTED = "call-not-connected"
EVENT_CALL_NOT_ANSWERED = "call-not-answered"
EVENT_CALL_REJECTED = "call-rejected"
EVENT_CALL_DISCONNECTED = "call-disconnected"
EVENT_CALL_DROPPED = "call-dropped"
EVENT_CALL_INPUT_RECEIVED = "call-input-received"
EVENT_CALL_AUDIO_RECORDING_RECEIVED = "call-audio-recording-received"
EVENT_FOLLOW_UP_CALL_NEVER_ANSWERED = "follow-up-call-never-answered"
EVENT_FOLLOW_UP_CALL_PREVIOUSLY_ANSWERED = "follow-up-call-previously-answered"
EVENT_FOLLOW_UPS_EXCEEDED = "follow-ups-exceeded"
EVENT_CALL_INPUT_TRIES_EXCEEDED = "call-input-tries-exceeded"


STEP_CLASSES = {
    STEP_SEND_EMAIL: SendEmailStep,
    STEP_SEND_SMS: SendSmsStep,
    STEP_DELAY: DelayStep,
    STEP_PLAY_MESSAGE: PlayMessageStep,
    STEP_QUESTIONS: QuestionsStep,
    STEP_GET_INPUT: GetInputStep,
    STEP_RECORD_AUDIO: RecordAudioStep,
    STEP_SET_STATUS: SetStatusStep,
    STEP_CALL: CallStep,
    STEP_HANG_UP: HangUpStep,
    STEP_RESUME_FROM_CHECKPOINT: ResumeFromCheckpointStep,
    STEP_GO_TO_FLOW: GoToFlowStep,
}


class Flow:
    def __init__(
        self, *, template=None, flow_json=None, id=None, name=None, call_max_tries=None
    ):
        self.template = template
        self.steps = []
        self.steps_by_id = {}
        self.events = []
        self.events_by_id = {}

        if flow_json:
            self.id = flow_json["id"]
            self.name = flow_json["name"]
            self.call_max_tries = None
            if "data" in flow_json:
                self.call_max_tries = flow_json["data"].get("maxTries")

            for step_json in flow_json["steps"]:
                step_class = STEP_CLASSES[step_json["type"]]
                step = step_class(flow=self, step_json=step_json)
                self.add_step(step)

            for event_json in flow_json.get("events"):
                event = Event(event_json=event_json)
                self.add_event(event)
        else:
            self.id = id
            self.name = name
            self.call_max_tries = call_max_tries

    def get_step(self, step_id):
        return self.steps_by_id.get(step_id)

    def get_step_by_name(self, step_name, case_insensitive=False):
        for step in self.steps:
            if (
                case_insensitive and step.name.lower() == step_name.strip().lower()
            ) or (not case_insensitive and step.name == step_name):
                return step
        return None

    def get_steps_by_type(self, step_type):
        steps = []
        for step in self.steps:
            if step.type == step_type:
                steps.append(step)
        return steps

    def add_step(self, step):
        self.steps.append(step)
        self.steps_by_id[step.id] = step

    def delete_step(self, step_to_delete):
        self.steps = [step for step in self.steps if step.id != step_to_delete.id]
        del self.steps_by_id[step_to_delete.id]
        for step in self.steps:
            step.delete_references_to_step(step_to_delete.id)
        for event in self.events:
            event.delete_references_to_step(step_to_delete.id)

    def get_event(self, event_id):
        return self.events_by_id.get(event_id)

    def add_event(self, event):
        self.events.append(event)
        self.events_by_id[event.id] = event

    def to_json(self):
        flow_json = {
            "id": self.id,
            "name": self.name,
            "events": [event.to_json() for event in self.events],
            "steps": [step.to_json() for step in self.steps],
        }
        if self.call_max_tries:
            flow_json["data"] = {}
            flow_json["data"]["maxTries"] = self.call_max_tries
        return flow_json


class Template:
    def __init__(
        self,
        *,
        template_json=None,
        start_flow_id=None,
        input_max_tries=None,
        no_input_message_name=None,
        invalid_input_message_name=None,
        input_tries_exceeded_message_name=None,
    ):
        self.flows = []
        self.flows_by_id = {}

        if template_json:
            self.start_flow_id = template_json.get("start")
            self.input_max_tries = template_json.get("inputMaxTries")
            self.no_input_message_name = template_json.get("noInputMessageName")
            self.invalid_input_message_name = template_json.get(
                "invalidInputMessageName"
            )
            self.input_tries_exceeded_message_name = template_json.get(
                "inputTriesExceededMessageName"
            )

            for flow_json in template_json.get("flows", []):
                flow = Flow(template=self, flow_json=flow_json)
                self.add_flow(flow)
        else:
            self.start_flow_id = start_flow_id
            self.input_max_tries = input_max_tries
            self.no_input_message_name = no_input_message_name
            self.invalid_input_message_name = invalid_input_message_name
            self.input_tries_exceeded_message_name = input_tries_exceeded_message_name

    def get_flow(self, flow_id):
        return self.flows_by_id.get(flow_id)

    def add_flow(self, flow):
        self.flows.append(flow)
        self.flows_by_id[flow.id] = flow

    def get_steps_by_type(self, step_type):
        steps = []
        for flow in self.flows:
            flow_steps = flow.get_steps_by_type(step_type)
            steps.extend(flow_steps)
        return steps

    def get_step_by_dynamic_options_attribute_name(
        self, dynamic_options_attribute_name
    ):
        step = None
        get_input_steps = self.get_steps_by_type(STEP_GET_INPUT)
        for get_input_step in get_input_steps:
            if get_input_step.purpose == GET_INPUT_PURPOSE_COLLECT_INFORMATION:
                if (
                    get_input_step.dynamic_options_attribute_name
                    == dynamic_options_attribute_name
                ):
                    step = get_input_step
                    break
        return step

    def get_result_names(self, excluded_step_id=None):
        result_names = set()

        get_input_steps = self.get_steps_by_type(STEP_GET_INPUT)
        for get_input_step in get_input_steps:
            if get_input_step.purpose == GET_INPUT_PURPOSE_COLLECT_INFORMATION:
                if not excluded_step_id or get_input_step.id != excluded_step_id:
                    result_names.add(get_input_step.result_name)

        record_audio_steps = self.get_steps_by_type(STEP_RECORD_AUDIO)
        for record_audio_step in record_audio_steps:
            if not excluded_step_id or record_audio_step.id != excluded_step_id:
                result_names.add(record_audio_step.result_name)

        return result_names

    def to_json(self):
        return {
            "start": self.start_flow_id,
            "inputMaxTries": self.input_max_tries,
            "noInputMessageName": self.no_input_message_name,
            "invalidInputMessageName": self.invalid_input_message_name,
            "inputTriesExceededMessageName": self.input_tries_exceeded_message_name,
            "flows": [flow.to_json() for flow in self.flows],
        }
