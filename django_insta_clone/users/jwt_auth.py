import jwt
import datetime

from django.conf import settings

def generate_jwt(user):
    payload = {
        'user_id' : user.user_id,
        'username' : user.username
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat' : datetime.datetime.utcnow()
    }
    return  jwt.encode(payload , settings.SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None