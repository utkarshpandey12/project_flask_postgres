from flask import Blueprint

common = Blueprint("common", __name__, template_folder="templates")

from . import views  # noqa: F401, E402
