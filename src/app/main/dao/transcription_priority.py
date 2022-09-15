import datetime

from ... import db
from ..models.main import Campaign, Org, TranscriptionPriority


def get_all_transcription_priorities():
    return (
        TranscriptionPriority.query.outerjoin(
            Org, TranscriptionPriority.org_id == Org.id
        )
        .outerjoin(Campaign, TranscriptionPriority.campaign_id == Campaign.id)
        .options(db.contains_eager(TranscriptionPriority.org))
        .options(db.contains_eager(TranscriptionPriority.campaign))
        .order_by(TranscriptionPriority.priority)
        .all()
    )


def get_transcription_priority(org, campaign, speaker, audio_type):
    return TranscriptionPriority.query.filter(
        TranscriptionPriority.org == org,
        TranscriptionPriority.campaign == campaign,
        TranscriptionPriority.speaker == speaker,
        TranscriptionPriority.audio_type == audio_type,
    ).first()


def get_transcription_priority_by_id(transcription_priority_id):
    return (
        TranscriptionPriority.query.outerjoin(
            Org, TranscriptionPriority.org_id == Org.id
        )
        .outerjoin(Campaign, TranscriptionPriority.campaign_id == Campaign.id)
        .options(db.contains_eager(TranscriptionPriority.org))
        .options(db.contains_eager(TranscriptionPriority.campaign))
        .filter(TranscriptionPriority.id == transcription_priority_id)
        .first()
    )


def create_transcription_priority(
    org, campaign, speaker, audio_type, priority, current_user
):
    now = datetime.datetime.now()
    priority_key_regex = TranscriptionPriority.build_priority_key_regex(
        org_id=org.id if org else None,
        campaign_id=campaign.id if campaign else None,
        speaker=speaker,
        audio_type=audio_type,
    )
    transcription_priority = TranscriptionPriority(
        org=org,
        campaign=campaign,
        speaker=speaker,
        audio_type=audio_type,
        priority=priority,
        priority_key_regex=priority_key_regex,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(transcription_priority)
    db.session.flush()
    return transcription_priority


def update_transcription_priority(transcription_priority, priority, current_user):
    transcription_priority.priority = priority
    transcription_priority.updated_at = datetime.datetime.now()
    transcription_priority.updated_by_user = current_user
    return transcription_priority


def delete_transcription_priority(transcription_priority):
    db.session.delete(transcription_priority)
