from flask.views import View
from flask import request, g, current_app, Response
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from jwt.exceptions import PyJWTError
from .utils import *
from . import models as gl_models



class User:
    def __init__(self, payload):
        self.id = payload['uid']
        self.jti = payload['jti']
        self.ati = payload['ati']
        self.exp = payload['exp']
        self.iat = payload['iat']

        self.db_reflection = g.db_session.query(gl_models.users).filter_by(id=self.id).one()

    @classmethod
    def from_id_token(cls, token):
        
        try:
            payload = verify_id_token(token)
        except (PyJWTError, KeyError):
            payload = None
        
        return None if payload is None else cls(payload)


class BaseEvent(View):
    endpoint_name = ""

    def __init__(self):
        print(current_app.config)
        cookie_name = current_app.config["ACCESS_TOKEN_NAME"]
        if cookie_name in request.cookies:
            g.user = User.from_id_token(request.cookies.get(cookie_name))
        else:
            g.user = None
        
        super().__init__()

    def on_get(self):
        # consider default urlfor
        abort(400)

    def on_post(self):
        abort(400)

    def onRequest(self, *args, **kwargs):
        
        if request.method == 'POST':
            response = self.on_post(*args, **kwargs)
        elif request.method == 'GET':
            response = self.on_get(*args, **kwargs)
        else:
            response = "Unknown method", 400
        
        return response

    def dispatch_request(self, *args, **kwargs):
        return self.onRequest(*args, **kwargs)

    @classmethod
    def get_rule_dict(cls):
        d = {
            "rule": "/" + cls.endpoint_name,
            "view_func": cls.as_view(cls.endpoint_name)
        }
        return d

    @classmethod
    def register_in_blueprint(cls, blueprint):
        blueprint.add_url_rule(**cls.get_rule_dict())


def login_required(http_method_handler):
    @functools.wraps
    def wrapped_handler(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return http_method_handler(*args, **kwargs)
    
    return wrapped_handler
