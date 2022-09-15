import datetime

from ... import db
from ..models.main import RecordingInstruction


def get_recording_instructions():
    return RecordingInstruction.query.all()


def get_recording_instruction_with_id(id):
    return RecordingInstruction.query.get(id)


def get_recording_instruction_with_type_and_name(instruction_type, name):
    query = RecordingInstruction.query.filter(
        RecordingInstruction.instruction_type == instruction_type,
    )
    if name:
        query = query.filter(
            db.func.lower(RecordingInstruction.name) == name.strip().lower()
        )
    return query.first()


def create_recording_instruction(
    name,
    instruction_type,
    audio_file_path,
    current_user,
):
    now = datetime.datetime.now()
    recording_instruction = RecordingInstruction(
        name=name,
        instruction_type=instruction_type,
        audio_file_path=audio_file_path,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(recording_instruction)
    db.session.flush()
    return recording_instruction
