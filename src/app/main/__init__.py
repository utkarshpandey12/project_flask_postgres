from flask import Blueprint

main = Blueprint("main", __name__, template_folder="templates")

from . import models, views  # noqa: F401, E402
