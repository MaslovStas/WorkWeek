from flask import Blueprint

bp = Blueprint('reserve', __name__)

from app.reserve import routes