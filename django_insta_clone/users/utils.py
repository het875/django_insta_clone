import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


# Decode JWT token and handle errors using SimpleJWT
def decode_jwt(token):
    try:
        # Decode the JWT token using SimpleJWT's AccessToken class (which validates automatically)
        access_token = AccessToken(token)
        return access_token.payload  # Returns the decoded payload

    except TokenError:
        return {'message': 'Invalid or expired token'}
    except Exception as e:
        return {'message': f'Token decoding error: {str(e)}'}

