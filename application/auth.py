import functools
from flask import (
    Blueprint, flash, g, 
    redirect, make_response, 
    render_template, request, 
    session, url_for, current_app
)
from .primitives import BaseEvent
from . import models as gl_models
from .utils import *

auth = Blueprint('auth', __name__, url_prefix='/auth')


class Register(BaseEvent):
    methods = ['POST', 'GET']
    endpoint_name = 'register'

    @staticmethod
    def on_get():
        return render_template('auth/register.html.j2')

    @staticmethod
    def on_post():
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not email:
            error = "Email is requied."
        elif g.db_session.query(gl_models.users).filter_by(name=username) \
            .one_or_none() is not None:
            
            error = "User {} already exists.".format(username)
        elif g.db_session.query(gl_models.users).filter_by(email=email) \
            .one_or_none() is not None:
            error = "User with email {} already exists.".format(email)
        
        if error is None:
            new_user = gl_models.users(name=username,
                                       email=email,
                                       confirmed=False)
            new_user.set_password(password)
            
            g.db_session.add(new_user)
            g.db_session.commit()

            return redirect(url_for('auth.login'))
        
        else:
            flash(error)


class Login(BaseEvent):
    methods = ['POST', 'GET']
    endpoint_name = "login"

    def on_post(self):
        username = request.form['username']
        password = request.form['password']

        error = None
        login_user = g.db_session.query(gl_models.users).filter_by(name=username).one_or_none()

        if login_user is None:
            error = 'Invalid credentials.'
        elif not login_user.check_password(password):
            error = 'Invalid credentials.'

        if error is None:
            
            response = make_response(redirect(url_for('blog.index')))
            response.set_cookie(current_app.config["ACCESS_TOKEN_NAME"],
                                build_access_token(login_user.id),
                                max_age=current_app.config["JWT_ACCESS_EXP"] - 5,
                                httponly=True)
            
            return response
        
        flash(error)
    
    def on_get(self):
        return render_template('auth/login.html.j2')


class Logout(BaseEvent):
    methods = ["GET"]
    endpoint_name = 'logout'

    def on_get(self):
        # TODO: Blacklist token
        response = make_response(redirect(url_for('blog.index')))
        response.set_cookie(current_app.config["ACCESS_TOKEN_NAME"],
                            '',
                            expires=0,
                            httponly=True)
        return response


Register.register_in_blueprint(auth)
Login.register_in_blueprint(auth)
Logout.register_in_blueprint(auth)

