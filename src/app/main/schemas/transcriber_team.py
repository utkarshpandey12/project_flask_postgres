from marshmallow import Schema, fields
from marshmallow.validate import Length

from .language import LanguageSchema
from .org import OrgSchema
from .user import UserSchema


class TranscriberTeamSchema(Schema):
    id = fields.Integer()
    name = fields.String(
        required=True,
        validate=[
            Length(
                min=1, max=80, error="Name must be between {min} and {max} characters"
            ),
        ],
        error_messages={
            "required": "Name is required",
            "null": "Name is required",
            "invalid": "Name must be a string",
        },
    )
    language = fields.Nested(
        LanguageSchema,
        required=True,
        error_messages={
            "required": "Language id is required",
            "null": "Language id is required",
            "invalid": "Language id must be a Integer",
        },
    )

    is_default = fields.Boolean(
        required=True,
        data_key="isDefault",
        error_messages={"required": "isDefault is required"},
    )
    transcribers = fields.Pluck(
        "TranscriberTeamUserSchema", "transcriber_user", many=True
    )


create_transcriber_team_schema = TranscriberTeamSchema(
    only=("name", "language.id", "is_default")
)


update_transcriber_team_schema = TranscriberTeamSchema(only=("name", "is_default"))


transcriber_team_schema = TranscriberTeamSchema(
    only=("id", "name", "language.id", "language.name", "is_default")
)


transcriber_team_details_schema = TranscriberTeamSchema(
    only=(
        "id",
        "name",
        "language.id",
        "language.name",
        "is_default",
        "transcribers",
    )
)


class TranscriberTeamUserSchema(Schema):
    transcriber_user = fields.Nested(
        UserSchema,
        data_key="user",
        required=True,
        error_messages={
            "required": "User is required",
            "null": "User is required",
            "invalid": "User data is required",
        },
    )


add_transcriber_schema = TranscriberTeamUserSchema(only=("transcriber_user.id",))


class TranscriberTeamOrgSchema(Schema):
    id = fields.Integer()
    transcriber_team_id = fields.Integer(
        data_key="transcriberTeamId",
        required=True,
        allow_none=False,
        error_messages={
            "required": "Transcriber Team Id is required",
            "null": "Transcriber Team Id is required",
            "invalid": "A valid Transcriber Team Id is required",
        },
    )
    transcriber_team = fields.Nested(TranscriberTeamSchema, data_key="transcriberTeam")
    org_id = fields.Integer(
        data_key="orgId",
        required=True,
        allow_none=False,
        error_messages={
            "required": "Org Id is required",
            "null": "Org Id is required",
            "invalid": "A valid Org Id is required",
        },
    )
    org = fields.Nested(OrgSchema)


add_transcriber_team_org_schema = TranscriberTeamOrgSchema(
    only=("transcriber_team_id", "org_id")
)

transcriber_team_org_schema = TranscriberTeamOrgSchema(
    only=(
        "id",
        "transcriber_team.id",
        "transcriber_team.name",
        "transcriber_team.language.id",
        "transcriber_team.language.name",
        "org.id",
        "org.name",
    )
)
