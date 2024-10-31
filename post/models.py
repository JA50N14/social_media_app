from django.db import models
from django.conf import settings

# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='user/%Y/%m/%d/')
    caption = models.TextField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post: {self.user.username} - {self.created}'

    def count_likes(self):
        return self.likes.filter(like=True).count()


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', related_name='replies', blank=True, null=True, on_delete=models.CASCADE)
    comment_text = models.TextField(max_length=150, verbose_name='Comment')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment: {self.user.username} - {self.created}'
    
    def count_likes(self):
        return self.likes.filter(like=True).count()

    def get_all_replies(self):
        return self.replies.all().order_by('-created')[:15]
    

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE, blank=True, null=True)
    like = models.BooleanField(default=False)

    def __str__(self):
        return f'Like: {self.like}'
    

class Follow(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follower', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.BooleanField(default=True)
    



