import jwt, uuid
from datetime import datetime
from flask import current_app as app

def build_access_token(uid):
    # ati - to identify refresh/access
    payload = {"jti": uuid.uuid4().hex,
               "ati": "access",
               "exp": int(datetime.now().timestamp() + app.config["JWT_ACCESS_EXP"]),
               "iat": int(datetime.now().timestamp()),
               "uid": uid}
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm='HS256')
    return token.decode("utf-8")


def verify_id_token(token, ati="access"):
    payload = jwt.decode(token, app.config["SECRET_KEY"])
    if payload["ati"] != ati:
        message = "Invalid ati claim. Token should be {} but is {}".format(ati, payload["ati"])
        raise jwt.exceptions.InvalidKeyError(message)
    return payload