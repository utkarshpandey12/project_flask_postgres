from ... import db
from ..models import main as constants
from ..models.main import TranscriptionPriority, TranscriptionTask


def update_transcription_task_priorities():
    priority_query = (
        db.select([TranscriptionPriority.priority])
        .where(
            TranscriptionTask.priority_key.regexp_match(
                TranscriptionPriority.priority_key_regex
            )
        )
        .order_by(TranscriptionPriority.priority)
        .limit(1)
    )
    TranscriptionTask.query.update(
        values={
            "priority": db.func.coalesce(
                priority_query, constants.DEFAULT_TRANSCRIPTION_PRIORITY
            )
        },
        synchronize_session=False,
    )
