from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password , check_password
from django.db import IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError


from .models import *
from .utils import *



import json
import jwt
from datetime import datetime , timedelta


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        try:
            # Create the user instance
            user = User(
                user_id=data['user_id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                username=data['username'],
                email=data['email'],
                mobile_number=data['mobile_number'],
                profile_picture=data['profile_picture'],
                dob=data['dob'],
                bio=data['bio'],
            )

            # Hash the password before saving
            user.password = make_password(data['password'])
            user.save()

            # Create the access and refresh tokens
            # refresh = RefreshToken.for_user(user)
            # access_token = str(refresh.access_token)
            # refresh_token = str(refresh)

            # Get the expiration time of the access token
            # access_token_expiry = datetime.utcnow() + timedelta(seconds=64000)

            # Prepare response with tokens and user data
            response_data = {
                # "access_token": access_token,
                # "refresh_token": refresh_token,
                # "access_token_expiry": access_token_expiry.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "user_data": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "profile_picture": user.profile_picture.url if user.profile_picture else None,
                    "dob": user.dob,
                    "bio": user.bio,
                }
            }

            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            if 'unique' in str(e).lower():
                if 'username' in str(e).lower() or 'email' in str(e).lower() or 'mobile_number' in str(e).lower() or 'user_id' in str(e).lower():
                    error_message = "Mobaile number or emaile is already exists."
                else:
                    error_message = "Duplicate data found."

                return JsonResponse({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({'Message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


# Login API
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'message': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Invalid credentials Username'}, status=status.HTTP_400_BAD_REQUEST)

        if check_password(password, user.password):
            # Generate JWT tokens using SimpleJWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Get the expiration time of the access token
            access_token_expiry = datetime.utcnow() + timedelta(seconds=6400)

            response_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_token_expiry": access_token_expiry.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "user_data": {
                    "user_id": user.user_id,
                    "username": user.username,
                }
            }

            return JsonResponse(response_data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Invalid Password credentials'}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'message': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)


# Get Profile API
def get_profile(request):
    # Extract the JWT token from the Authorization header
    token = request.headers.get('Authorization')

    if token:
        # Extract the token from "Bearer <token>"
        token = token.split(' ')[1]
        #print(f"Received token: {token}")  # Debugging

        try:
            # Decode the JWT token using SimpleJWT's AccessToken class
            access_token = AccessToken(token)
            user_id = access_token['user_id']  # Extract user_id from the token

            # If token is valid, fetch the user from the database using the user ID
            try:
                user = User.objects.get(id=user_id)
                # Return user details as JSON response
                return JsonResponse({
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'bio': user.bio,
                    'dob': user.dob,
                    'mobile_number': user.mobile_number,
                })
            except User.DoesNotExist:
                return JsonResponse({'message': 'User not found'}, status=404)

        except TokenError:
            return JsonResponse({'message': 'Invalid or expired token, or user_id missing'}, status=401)

    return JsonResponse({'message': 'Authorization token missing'}, status=401)



