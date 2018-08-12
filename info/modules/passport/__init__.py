from flask import Blueprint

passport_blue = Blueprint('passport', __name__)

from . import views