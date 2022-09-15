from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from ..models import main as constants
from .campaign import CampaignSchema
from .org import OrgSchema


class TranscriptionPrioritySchema(Schema):
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
    org = fields.Nested(OrgSchema)
    campaign_id = fields.Integer(
        data_key="campaignId",
        required=True,
        allow_none=True,
        error_messages={
            "required": "Campaign Id is required",
            "invalid": "A valid Campaign Id is required",
        },
    )
    campaign = fields.Nested(CampaignSchema)
    speaker = fields.String(
        required=True,
        allow_none=True,
        validate=OneOf(
            [
                constants.SPEAKER_CANDIDATE,
                constants.SPEAKER_CAMPAIGN_OWNER,
            ],
            error="Speaker must be one of - {choices}.",
        ),
    )
    audio_type = fields.String(
        data_key="audioType",
        required=True,
        allow_none=True,
        validate=OneOf(
            [
                constants.AUDIO_TYPE_QUESTION,
                constants.AUDIO_TYPE_ANSWER,
                constants.AUDIO_TYPE_MESSAGE,
            ],
            error="Audio Type must be one of - {choices}.",
        ),
    )
    priority = fields.Integer(
        required=True,
        error_messages={
            "required": "Priority is required",
            "null": "Priority is required",
            "invalid": "A valid priority is required",
        },
    )


transcription_priority_schema = TranscriptionPrioritySchema(
    only=(
        "id",
        "org.id",
        "org.name",
        "campaign.id",
        "campaign.name",
        "speaker",
        "audio_type",
        "priority",
    )
)

create_transcription_priority_schema = TranscriptionPrioritySchema(
    only=("org_id", "campaign_id", "speaker", "audio_type", "priority")
)

update_transcription_priority_schema = TranscriptionPrioritySchema(only=("priority",))
