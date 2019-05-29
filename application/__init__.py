import os

from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE= 'postgresql://diana:DarzBor47!@localhost:5432/diana_database'
    )

    if test_config is None:
        # load the config if it exists when not testing
        app.config.from_pyfile('config.py', silent=True)

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
        g.db_session.commit()
        Session.remove()
    
    @app.route('/hello')
    def hello():
        return 'Darz bór!'

    return app
