from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from flask_login import current_user, login_user, login_required, logout_user
from . import settings
encryption_method = settings.encryption_method

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('view_pages.profile'))



@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    wallet = request.form.get('btc_wallet')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    new_user = User(email=email, name=name, password=generate_password_hash(password, method=encryption_method), btc_address=wallet)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('view_pages.index'))

@auth.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@auth.route('/settings', methods=['POST'])
@login_required
def settings_post():
    new_name = request.form.get('name','')
    new_wallet = request.form.get('btc_wallet','')
    new_password = request.form.get('password','')
    old_password = request.form.get('old_password','')
    if check_password_hash(current_user.password, old_password):
        if len(new_name) > 0:
            current_user.name = new_name
        if len(new_wallet) > 0:
            current_user.btc_address = new_wallet
        if len(new_password) > 0:
            current_user.password = generate_password_hash(new_password, method=encryption_method)
        db.session.commit()
        return redirect(url_for('view_pages.profile'))
    flash('Please check your password and try again.')
    return redirect(url_for('auth.settings'))