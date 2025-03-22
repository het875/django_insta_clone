from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import json

from .models import Post, Comment
from users.models import *
from users.utils import *



@csrf_exempt  # If you're using Postman and bypassing CSRF protection
def create_post(request):
    if request.method == 'POST':
        # Extract the JWT token from the Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'message': 'Authorization token missing'}, status=401)

        # Extract the token from "Bearer <token>"
        token = token.split(' ')[1]

        # Decode the JWT token and get the payload
        payload = decode_jwt(token)

        if 'user_id' not in payload:
            return JsonResponse({'message': 'Invalid or expired token'}, status=401)

        # Fetch the user from the database using the user_id from the payload
        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)

        try:
            # Get the post data from the request body
            data = json.loads(request.body)

            # Extract the caption from the request data
            caption = data.get('caption', '')

            # If you're sending an image as part of a POST request, use `request.FILES`
            image = request.FILES.get('media', None)

            # Create the post in the database
            post = Post.objects.create(
                user=user,
                caption=caption,
                media=image
            )

            # Return the created post as a JSON response
            return JsonResponse({
                'id': post.id,
                'caption': post.caption,
                'media_url': post.media.url if post.media else None,
                'created_at': post.created_at,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Error creating post: {str(e)}'}, status=400)


# Get Post API (with comments)
def get_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)

        # Get all top-level comments for the post
        comments = Comment.objects.filter(post=post, parent=None)

        # Prepare the response data for comments
        comments_data = []
        for comment in comments:
            replies = Comment.objects.filter(parent=comment)

            # Format replies
            replies_data = [{
                'id': reply.id,
                'user_id': reply.user.id,
                'username': reply.user.username,
                'text': reply.text,
                'created_at': reply.created_at,
                'updated_at': reply.updated_at
            } for reply in replies]

            comments_data.append({
                'id': comment.id,
                'user_id': comment.user.id,
                'username': comment.user.username,
                'text': comment.text,
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
                'replies': replies_data
            })

        # Return the post and its comments as JSON
        return JsonResponse({
            'id': post.id,
            'user_id': post.user.id,
            'username': post.user.username,
            'caption': post.caption,
            'image_url': post.media.url if post.media else None,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
            'comments': comments_data
        }, status=200)

    except Post.DoesNotExist:
        return JsonResponse({'message': 'Post not found'}, status=404)

# Create Comment API
@csrf_exempt
@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        parent_comment_id = request.POST.get('parent_comment_id')

        # Find the post by ID
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'message': 'Post not found'}, status=404)

        # Create a top-level or nested comment
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                comment = Comment.objects.create(user=request.user, post=post, text=text, parent=parent_comment)
            except Comment.DoesNotExist:
                return JsonResponse({'message': 'Parent comment not found'}, status=404)
        else:
            comment = Comment.objects.create(user=request.user, post=post, text=text)

        # Return the created comment as a JSON response
        return JsonResponse({
            'id': comment.id,
            'user_id': comment.user.id,
            'username': comment.user.username,
            'text': comment.text,
            'created_at': comment.created_at,
            'updated_at': comment.updated_at
        }, status=201)

    return JsonResponse({'message': 'Method not allowed'}, status=405)

