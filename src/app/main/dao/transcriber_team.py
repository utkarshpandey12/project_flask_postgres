import datetime

from sqlalchemy.sql.expression import true

from ... import db
from ..models.main import TranscriberTeam, TranscriberTeamOrg, TranscriberTeamUser


def create_transcriber_team(name, language, is_default, current_user):
    now = datetime.datetime.now()
    transcriber_team = TranscriberTeam(
        name=name,
        language=language,
        is_default=is_default,
        created_at=now,
        created_by_user=current_user,
        updated_at=now,
        updated_by_user=current_user,
    )
    db.session.add(transcriber_team)
    db.session.flush()
    return transcriber_team


def update_transcriber_team(transcriber_team, name, is_default, current_user):
    transcriber_team.name = name
    transcriber_team.is_default = is_default
    transcriber_team.updated_by_user = current_user
    transcriber_team.updated_at = datetime.datetime.now()
    return transcriber_team


def update_transcriber_teams_by_language_id(language_id, is_default):
    TranscriberTeam.query.filter(TranscriberTeam.language_id == language_id).update(
        {TranscriberTeam.is_default: is_default}, synchronize_session=False
    )


def get_transcriber_team_with_id(id):
    return TranscriberTeam.query.get(id)


def get_transcriber_team_by_name(name):
    return TranscriberTeam.query.filter(
        db.func.lower(TranscriberTeam.name) == name.strip().lower()
    ).first()


def get_default_transcriber_team_by_language_id(language_id):
    return TranscriberTeam.query.filter(
        TranscriberTeam.language_id == language_id, TranscriberTeam.is_default == true()
    ).first()


def get_all_transcriber_teams():
    return TranscriberTeam.query.all()


def get_transcriber_team_user(transcriber_team_id, user_id):
    return TranscriberTeamUser.query.filter(
        TranscriberTeamUser.transcriber_team_id == transcriber_team_id,
        TranscriberTeamUser.transcriber_user_id == user_id,
    ).first()


def add_transcriber_team_user(transcriber_team, user):
    now = datetime.datetime.now()
    transcriber_team_user = TranscriberTeamUser(
        transcriber_team=transcriber_team,
        transcriber_user=user,
        created_at=now,
    )
    db.session.add(transcriber_team_user)
    db.session.flush()
    return transcriber_team_user


def delete_transcriber_team_user(transcriber_team_user):
    db.session.delete(transcriber_team_user)
    db.session.flush()


def get_all_transcriber_team_orgs():
    return TranscriberTeamOrg.query.all()


def get_transcriber_team_org_with_id(transcriber_team_org_id):
    return TranscriberTeamOrg.query.get(transcriber_team_org_id)


def get_transcriber_team_org_with_team_id_and_org_id(transcriber_team_id, org_id):
    return TranscriberTeamOrg.query.filter(
        TranscriberTeamOrg.transcriber_team_id == transcriber_team_id,
        TranscriberTeamOrg.org_id == org_id,
    ).first()


def get_transcriber_team_org_with_org_id_and_language_id(org_id, language_id):
    return (
        TranscriberTeamOrg.query.join(
            TranscriberTeam,
            TranscriberTeam.id == TranscriberTeamOrg.transcriber_team_id,
        )
        .filter(
            TranscriberTeam.language_id == language_id,
            TranscriberTeamOrg.org_id == org_id,
        )
        .first()
    )


def add_transcriber_team_org(transcriber_team, org):
    now = datetime.datetime.now()
    transcriber_team_org = TranscriberTeamOrg(
        transcriber_team=transcriber_team,
        org=org,
        created_at=now,
    )
    db.session.add(transcriber_team_org)
    db.session.flush()
    return transcriber_team_org


def delete_transcriber_team_org(transcriber_team_org):
    db.session.delete(transcriber_team_org)
    db.session.flush()
