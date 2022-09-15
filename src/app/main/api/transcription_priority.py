from marshmallow.exceptions import ValidationError

from ...utils import response
from ..dao import campaign as campaign_dao
from ..dao import org as org_dao
from ..dao import transcription_priority as transcription_priority_dao
from ..dao import transcription_task as transcription_task_dao
from ..models import main as constants
from ..schemas import transcription_priority as transcription_priority_schemas


def get_transcription_priorities():
    transcription_priorities = (
        transcription_priority_dao.get_all_transcription_priorities()
    )
    res = transcription_priority_schemas.transcription_priority_schema.dump(
        transcription_priorities, many=True
    )
    return response.success(res)


def get_transcription_priority(transcription_priority_id):
    transcription_priority = (
        transcription_priority_dao.get_transcription_priority_by_id(
            transcription_priority_id
        )
    )
    if not transcription_priority:
        return response.not_found()

    res = transcription_priority_schemas.transcription_priority_schema.dump(
        transcription_priority
    )
    return response.success(res)


def create_transcription_priority(data, current_user):
    try:
        data = transcription_priority_schemas.create_transcription_priority_schema.load(
            data
        )
    except ValidationError as e:
        return response.validation_failed(e.messages)

    org_id = data.get("org_id")
    campaign_id = data.get("campaign_id")
    speaker = data.get("speaker")
    audio_type = data.get("audio_type")
    priority = data.get("priority")

    errors = {}

    org = None
    if org_id:
        org = org_dao.get_org_with_id(org_id)
        if not org:
            errors["orgId"] = ["Invalid org id."]

    campaign = None
    if campaign_id:
        campaign = campaign_dao.get_campaign_with_id(campaign_id)
        if not campaign:
            errors["campaignId"] = ["Invalid campaign id."]

    if speaker == constants.SPEAKER_CANDIDATE:
        if audio_type != constants.AUDIO_TYPE_ANSWER:
            errors["audioType"] = [f"Audio Type must be {constants.AUDIO_TYPE_ANSWER}"]
    elif speaker == constants.SPEAKER_CAMPAIGN_OWNER:
        if audio_type not in (
            constants.AUDIO_TYPE_QUESTION,
            constants.AUDIO_TYPE_MESSAGE,
        ):
            errors["audioType"] = [
                f"Audio Type must be one of - "
                f"{constants.AUDIO_TYPE_QUESTION}, {constants.AUDIO_TYPE_MESSAGE}"
            ]

    if errors:
        return response.validation_failed(errors)

    transcription_priority = transcription_priority_dao.get_transcription_priority(
        org, campaign, speaker, audio_type
    )

    if transcription_priority:
        errors[
            "message"
        ] = "Transcription priority already exists for the specified parameters"

    if errors:
        return response.validation_failed(errors)

    transcription_priority = transcription_priority_dao.create_transcription_priority(
        org, campaign, speaker, audio_type, priority, current_user
    )
    transcription_task_dao.update_transcription_task_priorities()
    res = transcription_priority_schemas.transcription_priority_schema.dump(
        transcription_priority
    )
    return response.success(res)


def update_transcription_priority(transcription_priority_id, data, current_user):
    transcription_priority = (
        transcription_priority_dao.get_transcription_priority_by_id(
            transcription_priority_id
        )
    )
    if not transcription_priority:
        return response.not_found()

    try:
        data = transcription_priority_schemas.update_transcription_priority_schema.load(
            data
        )
    except ValidationError as e:
        return response.validation_failed(e.messages)

    priority = data.get("priority")

    transcription_priority = transcription_priority_dao.update_transcription_priority(
        transcription_priority, priority, current_user
    )
    transcription_task_dao.update_transcription_task_priorities()
    res = transcription_priority_schemas.transcription_priority_schema.dump(
        transcription_priority
    )
    return response.success(res)


def delete_transcription_priority(transcription_priority_id, current_user):
    transcription_priority = (
        transcription_priority_dao.get_transcription_priority_by_id(
            transcription_priority_id
        )
    )
    if not transcription_priority:
        return response.not_found()

    transcription_priority_dao.delete_transcription_priority(transcription_priority)
    transcription_task_dao.update_transcription_task_priorities()
    return response.success({})
