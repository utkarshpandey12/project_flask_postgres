import shortuuid
from marshmallow.exceptions import ValidationError
from slugify import slugify

from ...utils import response, s3
from ..dao import recording_instruction as recording_instruction_dao
from ..models import main as constants
from ..schemas import recording_instruction as recording_instruction_schemas


def get_recording_instructions():
    recording_instructions = recording_instruction_dao.get_recording_instructions()
    res = recording_instruction_schemas.recording_instruction_schema.dump(
        recording_instructions, many=True
    )
    return response.success(res)


S3_PATH_RECORDING_INSTRUCTION = "audio/ri/{instruction_type}/{file_name}"


def create_recording_instruction(data, audio_file, current_user):
    try:
        data = recording_instruction_schemas.create_recording_instruction_schema.load(
            data
        )
    except ValidationError as e:
        return response.validation_failed(e.messages)

    instruction_type = data.get("instruction_type")
    name = data.get("name")

    errors = {}
    data_errors = {}
    errors["data"] = data_errors

    if not audio_file:
        errors["audioFile"] = ["Audio File is required"]

    if instruction_type == constants.RECORDING_INSTRUCTION_TYPE_OTHER:
        if not name:
            data_errors["name"] = ["Name is required"]
    else:
        if name:
            data_errors["name"] = [
                f"Name must not be provided for instruction type {instruction_type}"
            ]

    if "audioFile" in errors or data_errors:
        if not data_errors:
            del errors["data"]
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

    existing_instruction = (
        recording_instruction_dao.get_recording_instruction_with_type_and_name(
            instruction_type,
            name
            if instruction_type == constants.RECORDING_INSTRUCTION_TYPE_OTHER
            else None,
        )
    )

    if existing_instruction:
        if instruction_type == constants.RECORDING_INSTRUCTION_TYPE_OTHER:
            data_errors["name"] = [
                "A recording instruction with this name already exists"
            ]
        else:
            data_errors["instructionType"] = [
                "A recording instruction with this type already exists"
            ]

    if "audioFile" in errors or data_errors:
        if not data_errors:
            del errors["data"]
        return response.validation_failed(errors)

    file_name_slug = slugify(file_name)
    file_uuid = shortuuid.uuid()
    file_name_for_s3 = f"{file_name_slug}-{file_uuid}.{file_ext}"
    audio_file_path = S3_PATH_RECORDING_INSTRUCTION.format(
        instruction_type=instruction_type.lower(),
        file_name=file_name_for_s3,
    )
    s3.upload_audio_to_s3(audio_file_path, audio_file, is_private=False)

    if instruction_type != constants.RECORDING_INSTRUCTION_TYPE_OTHER:
        name = constants.RECORDING_INSTRUCTION_TYPE_NAMES[instruction_type]

    message = recording_instruction_dao.create_recording_instruction(
        name,
        instruction_type,
        audio_file_path,
        current_user,
    )
    res = recording_instruction_schemas.recording_instruction_schema.dump(message)
    return response.success(res)
