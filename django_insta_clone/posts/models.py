from django.db import models
from users.models import User


# Post model definition
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the post
    caption = models.TextField()  # Post caption/text
    media = models.FileField(upload_to='posts/')  # Media (image/video/file) uploaded
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set update timestamp

    def __str__(self):
        return f"Post {self.id} by {self.user.username}"

# Comment model definition
class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)  # User who commented
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)  # Post being commented on
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)  # For nested comments
    text = models.TextField()  # Comment content
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set update timestamp

    def __str__(self):
        return f"Comment {self.id} on Post {self.post.id} by {self.user.username}"

