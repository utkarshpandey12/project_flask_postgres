from marshmallow import Schema, fields
from marshmallow.validate import Length, OneOf

from ..models import main as constants


class RecordingInstructionSchema(Schema):
    id = fields.Integer()
    name = fields.String(
        required=True,
        allow_none=True,
        validate=[
            Length(
                min=1, max=100, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "invalid": "Name must be a string",
        },
    )
    instruction_type = fields.String(
        data_key="instructionType",
        required=True,
        validate=OneOf(
            [
                constants.RECORDING_INSTRUCTION_TYPE_WELCOME,
                constants.RECORDING_INSTRUCTION_TYPE_Q1,
                constants.RECORDING_INSTRUCTION_TYPE_Q2,
                constants.RECORDING_INSTRUCTION_TYPE_Q3,
                constants.RECORDING_INSTRUCTION_TYPE_Q4,
                constants.RECORDING_INSTRUCTION_TYPE_Q5,
                constants.RECORDING_INSTRUCTION_TYPE_Q6,
                constants.RECORDING_INSTRUCTION_TYPE_Q7,
                constants.RECORDING_INSTRUCTION_TYPE_Q8,
                constants.RECORDING_INSTRUCTION_TYPE_Q9,
                constants.RECORDING_INSTRUCTION_TYPE_Q10,
                constants.RECORDING_INSTRUCTION_TYPE_Q11,
                constants.RECORDING_INSTRUCTION_TYPE_Q12,
                constants.RECORDING_INSTRUCTION_TYPE_THANK_YOU,
                constants.RECORDING_INSTRUCTION_TYPE_OTHER,
            ],
            error="Instruction Type must be one of - {choices}.",
        ),
    )
    audio_file_url = fields.String(data_key="audioFileUrl")


recording_instruction_schema = RecordingInstructionSchema(
    only=(
        "id",
        "name",
        "instruction_type",
        "audio_file_url",
    )
)


create_recording_instruction_schema = RecordingInstructionSchema(
    only=(
        "name",
        "instruction_type",
    )
)
