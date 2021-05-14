from flask import Blueprint

social_blueprint = Blueprint('social', __name__, template_folder='templates')

from . import routes, events
