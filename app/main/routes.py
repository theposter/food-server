from app import db
from app.main import main_blueprint
from app.models import User
from flask import render_template
from flask_login import login_required

@main_blueprint.route('/')
@main_blueprint.route('/index')
def index():
     return render_template('index.html', title="Home Page")