import datetime

from flask import current_app
from flask_login import UserMixin
from sqlalchemy.dialects import postgresql

from ... import argon2, db
from ...utils import phone_number, s3


class Timezone(db.Model):
    __tablename__ = "d_timezone"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    all_identifiers = db.Column(postgresql.ARRAY(db.Text, dimensions=1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    @property
    def other_identifiers(self):
        return [
            other_identifier
            for other_identifier in self.all_identifiers
            if other_identifier != self.identifier
        ]


class Country(db.Model):
    __tablename__ = "d_country"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    country_code = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


class CountryTimezone(db.Model):
    __tablename__ = "d_country_timezone"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    timezone_id = db.Column(
        db.Integer, db.ForeignKey("d_timezone.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)

    country = db.relationship("Country")
    timezone = db.relationship("Timezone")

    __table_args__ = (
        db.UniqueConstraint("country_id", "timezone_id", name="uc_d_country_timezone"),
    )


class UnknownTimezone(db.Model):
    __tablename__ = "d_unknown_timezone"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    identifier = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


class State(db.Model):
    __tablename__ = "d_state"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)

    country = db.relationship("Country")


class City(db.Model):
    __tablename__ = "d_city"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    state_id = db.Column(
        db.Integer, db.ForeignKey("d_state.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)

    state = db.relationship("State")

    @property
    def fully_qualified_name(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"


class Language(db.Model):
    __tablename__ = "d_language"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False)


TELEPHONY_PROVIDER_TWILIO = "TWILIO"
TELEPHONY_PROVIDER_KOOKOO = "KOOKOO"


class TelephonyProvider(db.Model):
    __tablename__ = "d_telephony_provider"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False)


class SmsProvider(db.Model):
    __tablename__ = "d_sms_provider"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "d_user"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(16), nullable=True)
    must_change_password = db.Column(db.Boolean, nullable=False)
    is_email_verified = db.Column(db.Boolean, nullable=False)
    is_sys_admin = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True
    )

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    # A functional index on User.email using func.lower() function needs to
    # be added. But Alembic does not recognize functional indices.
    # So the code to create the functional index has been manually added to
    # db/versions/<Revision ID>_add_user.py

    def set_password(self, password):
        self.password = argon2.generate_password_hash(password)

    def verify_password(self, password):
        return argon2.check_password_hash(self.password, password)

    @property
    def country_code(self):
        return phone_number.get_country_code(self.mobile)

    @property
    def mobile_no(self):
        return phone_number.get_phone_number(self.mobile)


class Session(db.Model):
    __tablename__ = "d_session"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    uuid = db.Column(db.String(22), nullable=False, unique=True, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)
    last_seen_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User")

    def is_valid(self):
        # If 'SESSION_MAX_AGE' is 0, don't invalidate session
        if current_app.config["SESSION_MAX_AGE"] <= 0:
            return True

        session_age = datetime.datetime.now() - self.last_seen_at
        session_age = session_age.total_seconds()
        return session_age < current_app.config["SESSION_MAX_AGE"]

    def refresh(self):
        self.last_seen_at = datetime.datetime.now()


MODULE_TYPE_CUSTOMER = "C"
MODULE_TYPE_ADMIN = "A"
MODULE_TYPE_TRANSCRIBER = "T"


class Module(db.Model):
    __tablename__ = "d_module"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True)
    module_type = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    permissions = db.relationship("Permission", backref="module")


class Permission(db.Model):
    __tablename__ = "d_permission"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    module_id = db.Column(
        db.Integer, db.ForeignKey("d_module.id"), nullable=False, index=True
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
    identifier = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False)

    @property
    def fully_qualified_identifier(self):
        return f"{self.module.identifier}.{self.identifier}"


class Org(db.Model):
    __tablename__ = "d_org"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    spoken_name = db.Column(db.String(100), nullable=True)
    uuid = db.Column(db.String(22), nullable=False, unique=True, index=True)
    timezone_id = db.Column(
        db.Integer, db.ForeignKey("d_timezone.id"), nullable=False, index=True
    )
    logo_path = db.Column(db.String(120), nullable=True)
    settings = db.Column(postgresql.JSONB, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    timezone = db.relationship("Timezone")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


ORG_USER_STATUS_ACTIVE = "A"
ORG_USER_STATUS_INACTIVE = "I"


class OrgUser(db.Model):
    __tablename__ = "d_org_user"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False, index=True
    )
    is_owner = db.Column(db.Boolean(), nullable=False)
    manager_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True, index=True
    )
    status = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    user = db.relationship("User", foreign_keys=[user_id])
    manager = db.relationship("User", foreign_keys=[manager_user_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        db.UniqueConstraint("org_id", "user_id", name="uc_d_org_user_org_user"),
    )


ROLE_TYPE_CUSTOMER = "C"
ROLE_TYPE_ADMIN = "A"
ROLE_TYPE_TRANSCRIBER = "T"


class Role(db.Model):
    __tablename__ = "d_role"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    name = db.Column(db.String(30), nullable=False)
    role_type = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class RolePermission(db.Model):
    __tablename__ = "d_role_permission"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    role_id = db.Column(
        db.Integer, db.ForeignKey("d_role.id"), nullable=False, index=True
    )
    permission_id = db.Column(
        db.Integer, db.ForeignKey("d_permission.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    role = db.relationship("Role")
    permission = db.relationship("Permission")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        db.UniqueConstraint(
            "org_id",
            "role_id",
            "permission_id",
            name="uc_d_role_permission_org_role_permission",
        ),
    )


class UserRole(db.Model):
    __tablename__ = "d_user_role"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False, index=True
    )
    role_id = db.Column(
        db.Integer, db.ForeignKey("d_role.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    user = db.relationship("User", foreign_keys=[user_id], backref="user_roles")
    role = db.relationship("Role")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        db.UniqueConstraint(
            "org_id", "user_id", "role_id", name="uc_d_user_role_org_user_role"
        ),
    )


RECORDING_INSTRUCTION_TYPE_WELCOME = "WE"
RECORDING_INSTRUCTION_TYPE_Q1 = "Q1"
RECORDING_INSTRUCTION_TYPE_Q2 = "Q2"
RECORDING_INSTRUCTION_TYPE_Q3 = "Q3"
RECORDING_INSTRUCTION_TYPE_Q4 = "Q4"
RECORDING_INSTRUCTION_TYPE_Q5 = "Q5"
RECORDING_INSTRUCTION_TYPE_Q6 = "Q6"
RECORDING_INSTRUCTION_TYPE_Q7 = "Q7"
RECORDING_INSTRUCTION_TYPE_Q8 = "Q8"
RECORDING_INSTRUCTION_TYPE_Q9 = "Q9"
RECORDING_INSTRUCTION_TYPE_Q10 = "Q10"
RECORDING_INSTRUCTION_TYPE_Q11 = "Q11"
RECORDING_INSTRUCTION_TYPE_Q12 = "Q12"
RECORDING_INSTRUCTION_TYPE_THANK_YOU = "TY"
RECORDING_INSTRUCTION_TYPE_OTHER = "OTH"

RECORDING_INSTRUCTION_TYPE_NAMES = {
    RECORDING_INSTRUCTION_TYPE_WELCOME: "Welcome",
    RECORDING_INSTRUCTION_TYPE_Q1: "Question 1",
    RECORDING_INSTRUCTION_TYPE_Q2: "Question 2",
    RECORDING_INSTRUCTION_TYPE_Q3: "Question 3",
    RECORDING_INSTRUCTION_TYPE_Q4: "Question 4",
    RECORDING_INSTRUCTION_TYPE_Q5: "Question 5",
    RECORDING_INSTRUCTION_TYPE_Q6: "Question 6",
    RECORDING_INSTRUCTION_TYPE_Q7: "Question 7",
    RECORDING_INSTRUCTION_TYPE_Q8: "Question 8",
    RECORDING_INSTRUCTION_TYPE_Q9: "Question 9",
    RECORDING_INSTRUCTION_TYPE_Q10: "Question 10",
    RECORDING_INSTRUCTION_TYPE_Q11: "Question 11",
    RECORDING_INSTRUCTION_TYPE_Q12: "Question 12",
    RECORDING_INSTRUCTION_TYPE_THANK_YOU: "Thank You",
}

RECORDING_INSTRUCTION_TYPE_QUESTIONS = [
    RECORDING_INSTRUCTION_TYPE_Q1,
    RECORDING_INSTRUCTION_TYPE_Q2,
    RECORDING_INSTRUCTION_TYPE_Q3,
    RECORDING_INSTRUCTION_TYPE_Q4,
    RECORDING_INSTRUCTION_TYPE_Q5,
    RECORDING_INSTRUCTION_TYPE_Q6,
    RECORDING_INSTRUCTION_TYPE_Q7,
    RECORDING_INSTRUCTION_TYPE_Q8,
    RECORDING_INSTRUCTION_TYPE_Q9,
    RECORDING_INSTRUCTION_TYPE_Q10,
    RECORDING_INSTRUCTION_TYPE_Q11,
    RECORDING_INSTRUCTION_TYPE_Q12,
]


class RecordingInstruction(db.Model):
    __tablename__ = "d_recording_instruction"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instruction_type = db.Column(db.String(3), nullable=False)
    audio_file_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @property
    def audio_file_url(self):
        return (
            s3.generate_url(key_name=self.audio_file_path, is_private=False)
            if self.audio_file_path
            else None
        )


class FlowCategory(db.Model):
    __tablename__ = "d_flow_category"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon_file_path = db.Column(db.String(200), nullable=True)
    sequence = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @property
    def icon_url(self):
        return (
            s3.generate_url(key_name=self.icon_file_path, is_private=False)
            if self.icon_file_path
            else None
        )


FLOW_TEMPLATE_STATUS_DRAFT = "D"
FLOW_TEMPLATE_STATUS_PUBLISHED = "P"
FLOW_TEMPLATE_STATUS_ARCHIVED = "A"


class FlowTemplate(db.Model):
    __tablename__ = "d_flow_template"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version_identifier = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=True)
    flow_category_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_category.id"), nullable=False
    )
    flow_spec = db.Column(postgresql.JSONB, nullable=False)
    status = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    flow_category = db.relationship("FlowCategory")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


FIELD_TYPE_TEXT = "TE"
FIELD_TYPE_INTEGER = "IN"
FIELD_TYPE_DATE = "DA"
FIELD_TYPE_TIME = "TI"
FIELD_TYPE_DATE_TIME = "DT"
FIELD_TYPE_DATE_RANGE = "DR"
FIELD_TYPE_TIME_RANGE = "TR"
FIELD_TYPE_SCHEDULE = "SC"
FIELD_TYPE_LIST = "LI"
FIELD_TYPE_SEARCHABLE_LIST = "SL"
FIELD_TYPE_FILE_UPLOAD = "FU"

FIELD_CITY = "CITY"


class Field(db.Model):
    __tablename__ = "d_field"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    identifier = db.Column(db.String(100), nullable=False, unique=True)
    field_type = db.Column(db.String(2), nullable=False)
    values = db.Column(postgresql.JSONB, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)


class FlowTemplateField(db.Model):
    __tablename__ = "d_flow_template_field"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )
    field_id = db.Column(
        db.Integer, db.ForeignKey("d_field.id"), nullable=False, index=True
    )
    is_mandatory = db.Column(db.Boolean, nullable=False)
    allow_multiple_values = db.Column(db.Boolean, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)

    flow_template = db.relationship("FlowTemplate", backref="flow_template_fields")
    field = db.relationship("Field", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint(
            "flow_template_id",
            "field_id",
            name="uc_d_flow_template_field_flow_template_field",
        ),
    )


class FlowTemplateStatus(db.Model):
    __tablename__ = "d_flow_template_status"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    is_final = db.Column(db.Boolean, nullable=False)
    is_positive = db.Column(db.Boolean, nullable=False)
    is_reattempt_allowed = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)

    flow_template = db.relationship("FlowTemplate")


EMAIL_FORMAT_TEXT = "T"
EMAIL_FORMAT_HTML = "H"


class EmailTemplate(db.Model):
    __tablename__ = "d_email_template"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=True, index=True
    )
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    email_format = db.Column(db.String(1), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body_text = db.Column(db.Text, nullable=True)
    body_html = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    flow_template = db.relationship("FlowTemplate")
    org = db.relationship("Org")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class SmsTemplate(db.Model):
    __tablename__ = "d_sms_template"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=True, index=True
    )
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    flow_template = db.relationship("FlowTemplate")
    org = db.relationship("Org")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


MESSAGE_TYPE_AUDIO_FROM_TEMPLATE = "AT"
MESSAGE_TYPE_AUDIO_FROM_CAMPAIGN = "AC"
MESSAGE_TYPE_TEXT_TO_SPEECH_STATIC = "TS"
MESSAGE_TYPE_TEXT_TO_SPEECH_DYNAMIC = "TD"


class FlowTemplateMessage(db.Model):
    __tablename__ = "d_flow_template_message"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    message_type = db.Column(db.String(2), nullable=False)
    message_text = db.Column(db.Text, nullable=True)
    audio_file_path = db.Column(db.String(200), nullable=True)
    attribute = db.Column(db.String(100), nullable=True)
    recording_instruction_id = db.Column(
        db.Integer,
        db.ForeignKey("d_recording_instruction.id"),
        nullable=True,
        index=True,
    )
    sequence = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    flow_template = db.relationship("FlowTemplate")
    org = db.relationship("Org")
    recording_instruction = db.relationship("RecordingInstruction")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @property
    def audio_file_url(self):
        return (
            s3.generate_url(key_name=self.audio_file_path, is_private=False)
            if self.audio_file_path
            else None
        )


class FlowTemplatePage(db.Model):
    __tablename__ = "d_flow_template_page"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    flow_id = db.Column(db.String(22), nullable=False)
    elements = db.Column(postgresql.JSONB, nullable=False)

    flow_template = db.relationship("FlowTemplate")


ATTRIBUTE_NO_OF_USERS = "NO_OF_USERS"
ATTRIBUTE_NO_OF_CAMPAIGNS = "NO_OF_CAMPAIGNS"
ATTRIBUTE_NO_OF_SIMULTANEOUS_CALLS = "NO_OF_SIMULTANEOUS_CALLS"
ATTRIBUTE_IS_TRANSCRIPTION_ENABLED = "IS_TRANSCRIPTION_ENABLED"
ATTRIBUTE_IS_COMMUNICATION_SCORE_ENABLED = "IS_COMMUNICATION_SCORE_ENABLED"
ATTRIBUTE_IS_TRANSCRIPTION_AND_COMMUNICATION_SCORE_SEPARATE = (
    "IS_TRANSCRIPTION_AND_COMMUNICATION_SCORE_SEPARATE"
)
ATTRIBUTE_COMMUNICATION_SCORE_AND_TRANSCRIPTION_RATIO = (
    "COMMUNICATION_SCORE_AND_TRANSCRIPTION_RATIO"
)

ATTRIBUTE_TYPE_INTEGER = "I"
ATTRIBUTE_TYPE_BOOLEAN = "B"


class Attribute(db.Model):
    __tablename__ = "d_attribute"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    identifier = db.Column(db.String(100), nullable=False, unique=True)
    attribute_type = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


class Plan(db.Model):
    __tablename__ = "d_plan"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    start_on = db.Column(db.Date, nullable=False)
    end_on = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class PlanModule(db.Model):
    __tablename__ = "d_plan_module"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    plan_id = db.Column(
        db.Integer, db.ForeignKey("d_plan.id"), nullable=False, index=True
    )
    module_id = db.Column(
        db.Integer, db.ForeignKey("d_module.id"), nullable=False, index=True
    )

    plan = db.relationship("Plan", backref="plan_modules")
    module = db.relationship("Module")

    __table_args__ = (
        db.UniqueConstraint(
            "plan_id", "module_id", name="uc_d_plan_module_plan_module"
        ),
    )


class PlanAttribute(db.Model):
    __tablename__ = "d_plan_attribute"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    plan_id = db.Column(
        db.Integer, db.ForeignKey("d_plan.id"), nullable=False, index=True
    )
    attribute_id = db.Column(
        db.Integer, db.ForeignKey("d_attribute.id"), nullable=False, index=True
    )
    int_value = db.Column(db.Integer, nullable=True)
    bool_value = db.Column(db.Boolean, nullable=True)

    plan = db.relationship("Plan", backref="plan_attributes")
    attribute = db.relationship("Attribute")

    __table_args__ = (
        db.UniqueConstraint(
            "plan_id", "attribute_id", name="uc_d_plan_attribute_plan_attribute"
        ),
    )


class PlanFlowTemplate(db.Model):
    __tablename__ = "d_plan_flow_template"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    plan_id = db.Column(
        db.Integer, db.ForeignKey("d_plan.id"), nullable=False, index=True
    )
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )

    plan = db.relationship("Plan", backref="plan_flow_templates")
    flow_template = db.relationship("FlowTemplate")

    __table_args__ = (
        db.UniqueConstraint(
            "plan_id",
            "flow_template_id",
            name="uc_d_plan_flow_template_plan_flow_template",
        ),
    )


class PlanCountry(db.Model):
    __tablename__ = "d_plan_country"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    plan_id = db.Column(
        db.Integer, db.ForeignKey("d_plan.id"), nullable=False, index=True
    )
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    telephony_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_telephony_provider.id"), nullable=False, index=True
    )

    plan = db.relationship("Plan", backref="plan_countries")
    country = db.relationship("Country")
    telephony_provider = db.relationship("TelephonyProvider")

    __table_args__ = (
        db.UniqueConstraint(
            "plan_id", "country_id", name="uc_d_plan_country_plan_country"
        ),
    )


class Subscription(db.Model):
    __tablename__ = "d_subscription"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    plan_id = db.Column(
        db.Integer, db.ForeignKey("d_plan.id"), nullable=False, index=True
    )
    start_on = db.Column(db.Date, nullable=False)
    end_on = db.Column(db.Date, nullable=False)
    renewal_grace_period_days = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    plan = db.relationship("Plan")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


INVITE_TRANSACTION_TYPE_SUBSCRIPTION = "SU"
INVITE_TRANSACTION_TYPE_TOP_UP = "TU"
INVITE_TRANSACTION_TYPE_ADJUSTMENT = "AD"
INVITE_TRANSACTION_TYPE_CONSUMED = "CO"
INVITE_TRANSACTION_TYPE_EXPIRED = "EX"


class InviteTransaction(db.Model):
    __tablename__ = "d_invite_transaction"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    subscription_id = db.Column(
        db.Integer, db.ForeignKey("d_subscription.id"), nullable=False, index=True
    )
    txn_on = db.Column(db.Date, nullable=False)
    txn_type = db.Column(db.String(2), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    subscription = db.relationship("Subscription")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class InviteBalance(db.Model):
    __tablename__ = "d_invite_balance"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True, unique=True
    )
    amount = db.Column(db.Integer, nullable=False)

    org = db.relationship("Org")


USER_INVITE_TRANSACTION_TYPE_SUBSCRIPTION = INVITE_TRANSACTION_TYPE_SUBSCRIPTION
USER_INVITE_TRANSACTION_TYPE_TOP_UP = INVITE_TRANSACTION_TYPE_TOP_UP
USER_INVITE_TRANSACTION_TYPE_ADJUSTMENT = INVITE_TRANSACTION_TYPE_ADJUSTMENT
USER_INVITE_TRANSACTION_TYPE_CONSUMED = INVITE_TRANSACTION_TYPE_CONSUMED
USER_INVITE_TRANSACTION_TYPE_EXPIRED = INVITE_TRANSACTION_TYPE_EXPIRED
USER_INVITE_TRANSACTION_TYPE_GRANT_OUT = "GO"
USER_INVITE_TRANSACTION_TYPE_GRANT_IN = "GI"
USER_INVITE_TRANSACTION_TYPE_REVOKE_OUT = "RO"
USER_INVITE_TRANSACTION_TYPE_REVOKE_IN = "RI"


class UserInviteTransaction(db.Model):
    __tablename__ = "d_user_invite_transaction"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    subscription_id = db.Column(
        db.Integer, db.ForeignKey("d_subscription.id"), nullable=False, index=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("d_user.id"), nullable=False)
    counterparty_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True
    )
    txn_on = db.Column(db.Date, nullable=False)
    txn_type = db.Column(db.String(2), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    subscription = db.relationship("Subscription")
    user = db.relationship("User", foreign_keys=[user_id])
    counterparty_user = db.relationship("User", foreign_keys=[counterparty_user_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class UserInviteBalance(db.Model):
    __tablename__ = "d_user_invite_balance"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False, index=True
    )
    amount = db.Column(db.Integer, nullable=False)

    org = db.relationship("Org")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint(
            "org_id", "user_id", name="uc_d_user_invite_balance_org_user"
        ),
    )


CALLER_ID_CALL_TYPE_INITIAL = "I"
CALLER_ID_CALL_TYPE_FOLLOW_UP = "F"


class CallerId(db.Model):
    __tablename__ = "d_caller_id"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    telephony_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_telephony_provider.id"), nullable=False, index=True
    )
    call_type = db.Column(db.String(1), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("d_user.id"), nullable=True)
    phone_no = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    country = db.relationship("Country")
    telephony_provider = db.relationship("TelephonyProvider")
    user = db.relationship("User", foreign_keys=[user_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @property
    def mobile(self):
        return phone_number.format_e164(self.country.country_code, self.phone_no)


CALLER_ID_HISTORY_ACTION_INSERT = "I"
CALLER_ID_HISTORY_ACTION_UPDATE = "U"
CALLER_ID_HISTORY_ACTION_DELETE = "D"


class CallerIdHistory(db.Model):
    __tablename__ = "d_caller_id_history"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    telephony_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_telephony_provider.id"), nullable=False, index=True
    )
    call_type = db.Column(db.String(1), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("d_user.id"), nullable=True)
    phone_no = db.Column(db.String(16), nullable=False)
    action = db.Column(db.String(1), nullable=True)
    action_at = db.Column(db.DateTime, nullable=False)
    action_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    country = db.relationship("Country")
    telephony_provider = db.relationship("TelephonyProvider")
    user = db.relationship("User", foreign_keys=[user_id])
    action_by_user = db.relationship("User", foreign_keys=[action_by_user_id])


class SenderId(db.Model):
    __tablename__ = "d_sender_id"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    sms_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_sms_provider.id"), nullable=False, index=True
    )
    value = db.Column(db.String(12), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    country = db.relationship("Country")
    sms_provider = db.relationship("SmsProvider")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    __table_args__ = (
        db.UniqueConstraint(
            "org_id",
            "country_id",
            "sms_provider_id",
            name="uc_d_sender_id_unique",
        ),
    )


class Candidate(db.Model):
    __tablename__ = "d_candidate"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(254), nullable=False)
    mobile = db.Column(db.String(16), nullable=False, unique=True)
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    timezone_id = db.Column(
        db.Integer, db.ForeignKey("d_timezone.id"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    country = db.relationship("Country")
    timezone = db.relationship("Timezone")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    # A functional index on Candidate.email using func.lower() function needs to
    # be added. But Alembic does not recognize functional indices.
    # So the code to create the functional index has been manually added to
    # db/versions/<Revision ID>_add_candidate.py

    @property
    def country_code(self):
        return phone_number.get_country_code(self.mobile)

    @property
    def mobile_no(self):
        return phone_number.get_phone_number(self.mobile)


CANDIDATE_ATTRIBUTE_FIRST_NAME = "FN"
CANDIDATE_ATTRIBUTE_LAST_NAME = "LN"
CANDIDATE_ATTRIBUTE_EMAIL = "EM"
CANDIDATE_ATTRIBUTE_MOBILE = "MO"


class CandidateAttribute(db.Model):
    __tablename__ = "d_candidate_attribute"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    attribute = db.Column(db.String(2), nullable=False)
    value = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    candidate = db.relationship("Candidate")


class OrgCandidate(db.Model):
    __tablename__ = "d_org_candidate"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    opt_out_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    candidate = db.relationship("Candidate")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])

    __table_args__ = (
        db.UniqueConstraint(
            "org_id", "candidate_id", name="uc_d_org_candidate_org_candidate"
        ),
    )


CAMPAIGN_STATUS_DRAFT = "D"
CAMPAIGN_STATUS_STARTED = "S"
CAMPAIGN_STATUS_ENDED = "E"

CAMPAIGN_STEP_DEFINE_CAMPAIGN = "DC"
CAMPAIGN_STEP_DEFINE_MESSAGES = "DM"
CAMPAIGN_STEP_DEFINE_QUESTIONS = "DQ"
CAMPAIGN_STEP_RECORD = "RE"
CAMPAIGN_STEP_UPLOAD_CANDIDATES = "UC"
CAMPAIGN_STEP_SCHEDULE_INITIAL_CALL = "IC"
CAMPAIGN_STEP_SCHEDULE_FOLLOW_UP_CALLS = "FC"


class Campaign(db.Model):
    __tablename__ = "d_campaign"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    flow_template_id = db.Column(
        db.Integer, db.ForeignKey("d_flow_template.id"), nullable=False, index=True
    )
    country_id = db.Column(
        db.Integer, db.ForeignKey("d_country.id"), nullable=False, index=True
    )
    timezone_id = db.Column(
        db.Integer, db.ForeignKey("d_timezone.id"), nullable=False, index=True
    )
    language_id = db.Column(
        db.Integer, db.ForeignKey("d_language.id"), nullable=False, index=True
    )
    owner_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False, index=True
    )
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    last_completed_step = db.Column(db.String(2), nullable=True)
    status = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    flow_template = db.relationship("FlowTemplate")
    country = db.relationship("Country")
    timezone = db.relationship("Timezone")
    language = db.relationship("Language")
    owner_user = db.relationship("User", foreign_keys=[owner_user_id])
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class CampaignField(db.Model):
    __tablename__ = "d_campaign_field"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    field_id = db.Column(
        db.Integer, db.ForeignKey("d_field.id"), nullable=False, index=True
    )
    values = db.Column(postgresql.JSONB, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    field = db.relationship("Field")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_id",
            "field_id",
            name="uc_d_campaign_field_campaign_field",
        ),
    )

    @property
    def absolute_values(self):
        if not self.values:
            return self.values

        abs_values = []
        for value in self.values:
            if isinstance(value, dict):
                file_path = value.get("filePath")
                if file_path:
                    abs_value = {}
                    abs_value.update(value)
                    abs_value["fileUrl"] = s3.generate_url(
                        key_name=file_path, is_private=False
                    )
                    del abs_value["filePath"]
                    abs_values.append(abs_value)
                else:
                    abs_values.append(value)
            else:
                abs_values.append(value)

        return abs_values


SPEAKER_CANDIDATE = "C"
SPEAKER_CAMPAIGN_OWNER = "O"

AUDIO_TYPE_QUESTION = "Q"
AUDIO_TYPE_ANSWER = "A"
AUDIO_TYPE_MESSAGE = "M"

AUDIO_STATUS_NOT_APPLICABLE = "NA"
AUDIO_STATUS_QUEUED = "QU"
AUDIO_STATUS_COMPLETED = "CO"
AUDIO_STATUS_OTHER_LANGUAGE = "OL"
AUDIO_STATUS_NOT_CLEAR = "NC"
AUDIO_STATUS_BLANK = "BL"
AUDIO_STATUS_NOT_RELEVANT = "NR"

PROVIDER_AUDIO_DOWNLOAD_STATUS_PENDING = "P"
PROVIDER_AUDIO_DOWNLOAD_STATUS_COMPLETED = "C"


class CampaignAudio(db.Model):
    __tablename__ = "d_campaign_audio"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    speaker = db.Column(db.String(1), nullable=False)
    audio_type = db.Column(db.String(1), nullable=False)
    provider_audio_url = db.Column(db.Text(), nullable=False)
    provider_audio_download_status = db.Column(db.String(1), nullable=False)
    audio_file_path = db.Column(db.String(200), nullable=True)
    audio_length_secs = db.Column(db.Integer(), nullable=True)
    transcription_status = db.Column(db.String(2), nullable=False)
    transcription = db.Column(db.Text(), nullable=True)
    comm_score_status = db.Column(db.String(2), nullable=True)
    comm_score = db.Column(db.Integer(), nullable=True)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")

    @property
    def audio_file_url(self):
        return (
            s3.generate_url(key_name=self.audio_file_path, is_private=False)
            if self.audio_file_path
            else self.provider_audio_url
        )


AUDIO_ACTION_TRANSCRIPTION_AND_COMMUNICATION_SCORE = "TC"
AUDIO_ACTION_TRANSCRIPTION = "TR"
AUDIO_ACTION_COMMUNICATION_SCORE = "CS"


class CampaignAudioAction(db.Model):
    __tablename__ = "d_campaign_audio_action"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    campaign_audio_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign_audio.id"), nullable=False, index=True
    )
    action = db.Column(db.String(2), nullable=False)
    task_queued_at = db.Column(db.DateTime, nullable=False)
    action_started_at = db.Column(db.DateTime, nullable=False)
    action_ended_at = db.Column(db.DateTime, nullable=False)
    action_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True, index=True
    )
    transcription_status = db.Column(db.String(2), nullable=True)
    transcription = db.Column(db.Text(), nullable=True)
    comm_score_status = db.Column(db.String(2), nullable=True)
    comm_score = db.Column(db.Integer(), nullable=True)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    campaign_audio = db.relationship("CampaignAudio")
    action_by_user = db.relationship("User", foreign_keys=[action_by_user_id])


CAMPAIGN_CONTENT_TYPE_QUESTION = AUDIO_TYPE_QUESTION
CAMPAIGN_CONTENT_TYPE_MESSAGE = AUDIO_TYPE_MESSAGE

CAMPAIGN_QUESTION_ANSWER_TYPE_AUDIO = "A"
CAMPAIGN_QUESTION_ANSWER_TYPE_OPTIONS = "O"

CAMPAIGN_QUESTION_OPTIONS_TYPE_RECORDED = "REC"
CAMPAIGN_QUESTION_OPTIONS_TYPE_TEXT_TO_SPEECH = "TTS"

CAMPAIGN_CONTENT_RECORDING_STATUS_PENDING = "P"
CAMPAIGN_CONTENT_RECORDING_STATUS_IN_PROGRESS = "I"
CAMPAIGN_CONTENT_RECORDING_STATUS_INCOMPLETE = "N"
CAMPAIGN_CONTENT_RECORDING_STATUS_COMPLETED = "C"


class CampaignContent(db.Model):
    __tablename__ = "d_campaign_content"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    content_type = db.Column(db.String(1), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    flow_template_message_id = db.Column(
        db.Integer,
        db.ForeignKey("d_flow_template_message.id"),
        nullable=True,
        index=True,
    )
    message_text = db.Column(db.Text(), nullable=True)
    question_set_id = db.Column(db.String(22), nullable=True)
    question_no = db.Column(db.Integer(), nullable=True)
    question_text = db.Column(db.Text(), nullable=True)
    answer_type = db.Column(db.String(1), nullable=True)
    ideal_answer = db.Column(db.Text(), nullable=True)
    options_type = db.Column(db.String(3), nullable=True)
    options = db.Column(postgresql.JSONB, nullable=True)
    campaign_audio_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign_audio.id"), nullable=True, index=True
    )
    recording_status = db.Column(db.String(3), nullable=True)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    flow_template_message = db.relationship("FlowTemplateMessage")
    campaign_audio = db.relationship("CampaignAudio")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_id",
            "flow_template_message_id",
            name="uc_d_campaign_content_message",
        ),
        db.UniqueConstraint(
            "campaign_id",
            "question_set_id",
            "question_no",
            name="uc_d_campaign_content_question",
        ),
    )

    @property
    def option_texts(self):
        return [option["text"] for option in self.options] if self.options else None


CALL_STATUS_QUEUED = "QU"
CALL_STATUS_IN_PROGRESS = "IP"
CALL_STATUS_COMPLETED = "CO"
CALL_STATUS_BUSY = "BU"
CALL_STATUS_NO_ANSWER = "NA"
CALL_STATUS_UNABLE_TO_CONNECT = "UC"
CALL_STATUS_ERROR = "ER"

CAMPAIGN_OWNER_CONTENT_RECORDING_STATUS_PENDING = "P"
CAMPAIGN_OWNER_CONTENT_RECORDING_STATUS_COMPLETED = "C"

CAMPAIGN_OWNER_CALL_RECORDING_STATUS_PENDING = "P"
CAMPAIGN_OWNER_CALL_RECORDING_STATUS_IN_PROGRESS = "I"
CAMPAIGN_OWNER_CALL_RECORDING_STATUS_INCOMPLETE = "N"
CAMPAIGN_OWNER_CALL_RECORDING_STATUS_COMPLETED = "C"


class CampaignOwnerCall(db.Model):
    __tablename__ = "d_campaign_owner_call"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    uuid = db.Column(db.String(22), nullable=False, unique=True, index=True)
    content_statuses = db.Column(postgresql.JSONB, nullable=False)
    from_mobile = db.Column(db.String(16), nullable=False)
    to_mobile = db.Column(db.String(16), nullable=False)
    telephony_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_telephony_provider.id"), nullable=False, index=True
    )
    queued_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    call_sid = db.Column(db.String(120), nullable=True)
    call_duration = db.Column(db.Integer, nullable=True)
    error = db.Column(db.Text(), nullable=True)
    call_status = db.Column(db.String(2), nullable=False)
    recording_status = db.Column(db.String(1), nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    telephony_provider = db.relationship("TelephonyProvider")


CAMPAIGN_CANDIDATE_SOURCE_TYPE_CV = "C"
CAMPAIGN_CANDIDATE_SOURCE_TYPE_EXCEL = "E"
CAMPAIGN_CANDIDATE_SOURCE_TYPE_API = "A"

CAMPAIGN_CANDIDATE_BATCH_INITIAL_SCHEDULE_TYPE_IMMEDIATE = "I"
CAMPAIGN_CANDIDATE_BATCH_INITIAL_SCHEDULE_TYPE_SCHEDULED = "S"

CAMPAIGN_CANDIDATE_BATCH_FOLLOW_UP_SCHEDULE_TYPE_AUTO = "A"
CAMPAIGN_CANDIDATE_BATCH_FOLLOW_UP_SCHEDULE_TYPE_SCHEDULED = "S"

CAMPAIGN_CANDIDATE_BATCH_STATUS_PROCESSED = "P"
CAMPAIGN_CANDIDATE_BATCH_STATUS_SCHEDULED = "S"


class CampaignCandidateBatch(db.Model):
    __tablename__ = "d_campaign_candidate_batch"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    source_type = db.Column(db.String(1), nullable=False)
    initial_schedule_type = db.Column(db.String(1), nullable=True)
    invite_on = db.Column(db.Date, nullable=True)
    invite_at = db.Column(db.Integer, nullable=True)
    follow_up_schedule_type = db.Column(db.String(1), nullable=True)
    follow_up_1_on = db.Column(db.Date, nullable=True)
    follow_up_1_at = db.Column(db.Integer, nullable=True)
    follow_up_2_on = db.Column(db.Date, nullable=True)
    follow_up_2_at = db.Column(db.Integer, nullable=True)
    follow_up_3_on = db.Column(db.Date, nullable=True)
    follow_up_3_at = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])


CANDIDATE_INVITE_STATUS_PENDING = "P"
CANDIDATE_INVITE_STATUS_QUEUED = "Q"
CANDIDATE_INVITE_STATUS_IN_PROGRESS = "I"
CANDIDATE_INVITE_STATUS_COMPLETED = "C"


class CampaignCandidateInvite(db.Model):
    __tablename__ = "d_campaign_candidate_invite"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_batch_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_batch.id"),
        nullable=True,
        index=True,
    )
    source_type = db.Column(db.String(1), nullable=False)
    invite_at = db.Column(db.DateTime, nullable=True)
    follow_up_1_at = db.Column(db.DateTime, nullable=True)
    follow_up_2_at = db.Column(db.DateTime, nullable=True)
    follow_up_3_at = db.Column(db.DateTime, nullable=True)
    attempt_count = db.Column(db.Integer(), nullable=False)
    invites_consumed = db.Column(db.Integer(), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    invite_status = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_batch = db.relationship("CampaignCandidateBatch")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])


class CampaignCandidateInviteTask(db.Model):
    __tablename__ = "d_campaign_candidate_invite_task"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    campaign_candidate_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_attempt.id"),
        nullable=True,
        index=True,
    )
    sequence = db.Column(db.Integer, nullable=False)
    invite_at = db.Column(db.DateTime, nullable=False)

    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    campaign_candidate_attempt = db.relationship("CampaignCandidateAttempt")


class CampaignCandidateInviteResponse(db.Model):
    __tablename__ = "d_campaign_candidate_invite_response"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    step_id = db.Column(db.String(22), nullable=True, index=True)
    question_content_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_content.id"),
        nullable=True,
        index=True,
    )
    campaign_audio_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign_audio.id"), nullable=True, index=True
    )
    value = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    question_content = db.relationship("CampaignContent")
    campaign_audio = db.relationship("CampaignAudio")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_candidate_invite_id",
            "step_id",
            name="uc_d_campaign_candidate_invite_response_step_id",
        ),
        db.UniqueConstraint(
            "campaign_candidate_invite_id",
            "question_content_id",
            name="uc_d_campaign_candidate_invite_response_question_content_id",
        ),
    )


class CampaignCandidateInviteStatus(db.Model):
    __tablename__ = "d_campaign_candidate_invite_status"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    flow_id = db.Column(db.String(22), nullable=False, index=True)
    flow_template_status_id = db.Column(
        db.Integer,
        db.ForeignKey("d_flow_template_status.id"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    flow_template_status = db.relationship("FlowTemplateStatus")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_candidate_invite_id",
            "flow_id",
            name="uc_d_campaign_candidate_invite_status",
        ),
    )


class CampaignCandidateAttempt(db.Model):
    __tablename__ = "d_campaign_candidate_attempt"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    attempt_no = db.Column(db.Integer, nullable=False)
    transient_data = db.Column(postgresql.JSONB, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")


class CampaignCandidateAttemptResponse(db.Model):
    __tablename__ = "d_campaign_candidate_attempt_response"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    campaign_candidate_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_attempt.id"),
        nullable=False,
        index=True,
    )
    step_id = db.Column(db.String(22), nullable=True, index=True)
    question_content_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_content.id"),
        nullable=True,
        index=True,
    )
    campaign_audio_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign_audio.id"), nullable=True, index=True
    )
    value = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    campaign_candidate_attempt = db.relationship("CampaignCandidateAttempt")
    question_content = db.relationship("CampaignContent")
    campaign_audio = db.relationship("CampaignAudio")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_candidate_attempt_id",
            "step_id",
            name="uc_d_campaign_candidate_attempt_response_step_id",
        ),
        db.UniqueConstraint(
            "campaign_candidate_attempt_id",
            "question_content_id",
            name="uc_d_campaign_candidate_attempt_response_question_content_id",
        ),
    )


class CampaignCandidateAttemptStatus(db.Model):
    __tablename__ = "d_campaign_candidate_attempt_status"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    campaign_candidate_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_attempt.id"),
        nullable=False,
        index=True,
    )
    flow_id = db.Column(db.String(22), nullable=False, index=True)
    flow_template_status_id = db.Column(
        db.Integer,
        db.ForeignKey("d_flow_template_status.id"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    campaign_candidate_attempt = db.relationship("CampaignCandidateAttempt")
    flow_template_status = db.relationship("FlowTemplateStatus")

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_candidate_attempt_id",
            "flow_id",
            name="uc_d_campaign_candidate_attempt_status",
        ),
    )


class CampaignCandidateCall(db.Model):
    __tablename__ = "d_campaign_candidate_call"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign.id"), nullable=False, index=True
    )
    candidate_id = db.Column(
        db.Integer, db.ForeignKey("d_candidate.id"), nullable=False, index=True
    )
    campaign_candidate_invite_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_invite.id"),
        nullable=False,
        index=True,
    )
    campaign_candidate_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign_candidate_attempt.id"),
        nullable=False,
        index=True,
    )
    uuid = db.Column(db.String(22), nullable=False, unique=True, index=True)
    from_mobile = db.Column(db.String(16), nullable=False)
    to_mobile = db.Column(db.String(16), nullable=False)
    telephony_provider_id = db.Column(
        db.Integer, db.ForeignKey("d_telephony_provider.id"), nullable=False, index=True
    )
    queued_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    call_sid = db.Column(db.String(120), nullable=True)
    call_duration = db.Column(db.Integer, nullable=True)
    error = db.Column(db.Text(), nullable=True)
    call_status = db.Column(db.String(2), nullable=False)

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    candidate = db.relationship("Candidate")
    campaign_candidate_invite = db.relationship("CampaignCandidateInvite")
    campaign_candidate_attempt = db.relationship("CampaignCandidateAttempt")
    telephony_provider = db.relationship("TelephonyProvider")


class TranscriberTeam(db.Model):
    __tablename__ = "d_transcriber_team"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    language_id = db.Column(
        db.Integer, db.ForeignKey("d_language.id"), nullable=False, index=True
    )
    is_default = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    language = db.relationship("Language")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])


class TranscriberTeamUser(db.Model):
    __tablename__ = "d_transcriber_team_user"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    transcriber_team_id = db.Column(
        db.Integer, db.ForeignKey("d_transcriber_team.id"), nullable=False, index=True
    )
    transcriber_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False)

    transcriber_team = db.relationship("TranscriberTeam", backref="transcribers")
    transcriber_user = db.relationship("User", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint(
            "transcriber_team_id",
            "transcriber_user_id",
            name="uc_d_transcriber_team_user_transcriber_team_transcriber_user",
        ),
    )


class TranscriberTeamOrg(db.Model):
    __tablename__ = "d_transcriber_team_org"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    transcriber_team_id = db.Column(
        db.Integer, db.ForeignKey("d_transcriber_team.id"), nullable=False, index=True
    )
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    transcriber_team = db.relationship("TranscriberTeam")
    org = db.relationship("Org")

    __table_args__ = (
        db.UniqueConstraint(
            "transcriber_team_id",
            "org_id",
            name="uc_d_transcriber_team_org_transcriber_team_org",
        ),
    )


class TranscriptionPriority(db.Model):
    __tablename__ = "d_transcription_priority"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("d_org.id"), nullable=True, index=True)
    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign.id"),
        nullable=True,
        index=True,
    )
    speaker = db.Column(db.String(1), nullable=True)
    audio_type = db.Column(db.String(1), nullable=True)
    priority_key_regex = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )
    updated_at = db.Column(db.DateTime, nullable=False)
    updated_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=False
    )

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    created_by_user = db.relationship("User", foreign_keys=[created_by_user_id])
    updated_by_user = db.relationship("User", foreign_keys=[updated_by_user_id])

    @staticmethod
    def build_priority_key_regex(
        *,
        org_id: int = None,
        campaign_id: int = None,
        speaker: str = None,
        audio_type: str = None,
    ) -> str:
        org_id_regex = f"{org_id}" if org_id else ".*"
        campaign_id_regex = f"{campaign_id}" if campaign_id else ".*"
        speaker_regex = speaker if speaker else ".*"
        audio_type_regex = audio_type if audio_type else ".*"
        return f"{org_id_regex}-{campaign_id_regex}-{speaker_regex}-{audio_type_regex}"

    @staticmethod
    def build_priority_key(
        *, org_id: int, campaign_id: int, speaker: str, audio_type: str
    ) -> str:
        return f"{org_id}-{campaign_id}-{speaker}-{audio_type}"


TRANSCRIPTION_TASK_TYPE_TRANSCRIPTION_AND_COMMUNICATION_SCORE = (
    AUDIO_ACTION_TRANSCRIPTION_AND_COMMUNICATION_SCORE
)
TRANSCRIPTION_TASK_TYPE_TRANSCRIPTION = AUDIO_ACTION_TRANSCRIPTION
TRANSCRIPTION_TASK_TYPE_COMMUNICATION_SCORE = AUDIO_ACTION_COMMUNICATION_SCORE

DEFAULT_TRANSCRIPTION_PRIORITY = 1000


class TranscriptionTask(db.Model):
    __tablename__ = "d_transcription_task"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    org_id = db.Column(
        db.Integer, db.ForeignKey("d_org.id"), nullable=False, index=True
    )
    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("d_campaign.id"),
        nullable=False,
        index=True,
    )
    campaign_audio_id = db.Column(
        db.Integer, db.ForeignKey("d_campaign_audio.id"), nullable=False, index=True
    )
    question_text = db.Column(db.Text, nullable=True)
    task_type = db.Column(db.String(2), nullable=False)
    transcriber_team_id = db.Column(
        db.Integer, db.ForeignKey("d_transcriber_team.id"), nullable=False, index=True
    )
    queued_at = db.Column(db.DateTime, nullable=False)
    priority_key = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    locked_at = db.Column(db.DateTime, nullable=True)
    locked_by_user_id = db.Column(
        db.Integer, db.ForeignKey("d_user.id"), nullable=True, index=True
    )

    org = db.relationship("Org")
    campaign = db.relationship("Campaign")
    campaign_audio = db.relationship("CampaignAudio")
    transcriber_team = db.relationship("TranscriberTeam")
    locked_by_user = db.relationship("User")
