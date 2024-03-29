import os

from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import InvalidRequestError
from .utils import *
from . import auth
from . import blog

def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE='postgresql://diana:DarzBor47!@localhost:5432/diana_database',
        JWT_ACCESS_EXP=120,
        ACCESS_TOKEN_NAME="ID_TOKEN"
    )

    if test_config is None:
        # load the config if it exists when not testing
        print("LOADING CONFIG")
        app.config.from_json('server_config.json', silent=False)

    else:
        # load the test config if passed
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # configure sqlalchemy to serve sessions
    engine = create_engine(app.config['DATABASE'])
    Session = scoped_session(sessionmaker(bind=engine))

    @app.before_request
    def expose_session():
        g.db_session = Session()

    @app.teardown_appcontext
    def shutdown_session(response_or_exc):
        try:
            g.db_session.commit()
        except InvalidRequestError:
            g.db_session.rollback()

        Session.remove()
    
    # register blueprints

    app.register_blueprint(auth.auth)
    app.register_blueprint(blog.blog)
    # index
    app.add_url_rule('/', endpoint='blog.index')

    @app.route('/hello')
    def hello():
        
        return 'Darz bór!' + str(build_access_token("BEST CAL EVER .308Win"))

    return app
