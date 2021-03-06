from app import bcrypt, db
from app.auth import auth_blueprint
from app.main import main_blueprint
from app.models import User
from app.auth.forms import LoginForm, SignupForm
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.index'))
    form = LoginForm()
    if form.validate_on_submit():
        db_user_object = db.get_user_by_username(form.username.data)
        if db_user_object is None:
            flash('Invalid username or password')
            return redirect(url_for('auth_blueprint.login'))
        user = User(db_user_object['username'], db_user_object['password'], db_user_object['_id'], db_user_object['email'])
        if not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth_blueprint.login'))
        login_user(user, remember=form.remember_me.data)
        user_preferences_obj = db.get_user_preferences_document(user.id)
        user.set_user_preferences({'postal_code': user_preferences_obj['postal_code'], 'lat_long': user_preferences_obj['lat_long'],
                                   'cuisine_preferences': user_preferences_obj['cuisine_preferences']})
        session['userInstance'] = user.toDict()
        print(f'userInstance')
        # An attacker could insert a URL to a malicious site in the next argument, so the application only redirects
        # when the URL is relative, which ensures that the redirect stays within the same site as the application. 
        # To determine if the URL is relative or absolute, I parse it with Werkzeug's url_parse() function 
        # and then check if the netloc component is set or not.
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_blueprint.index')
        return redirect(next_page)
    return render_template('auth/login.html', title="Log in", form=form)

@auth_blueprint.route('/logout')
def logout():
    logout_user()
    session.pop('userInstance', None)
    return redirect(url_for('main_blueprint.index'))

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        encrypted_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = db.add_user({'username': form.username.data, 'password': str(encrypted_pwd), 'email': form.email.data})
        user = User(form.username.data, str(encrypted_pwd), user_id, form.email.data)
        login_user(user, remember=True)
        session['userInstance'] = user.toDict()
        return redirect(url_for('user_profile_blueprint.get_additional_info'))
    return render_template('auth/signup.html', title="Sign in", form=form)