from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import re
from django.urls import reverse
from django.db.models import UniqueConstraint

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
    
    @property
    def processed_caption(self):
        def replace_tag(match):
            username = match.group(1)
            try:
                user = User.objects.get(username=username)
                return f'<a class="user-link" href="{reverse("post:detail_profile_view", kwargs={"user_id": user.id})}">@{username}</a>'
            except User.DoesNotExist:
                return f'<a class="user-link" href="#">@{username}</a>'
            
        pattern = r"@([\w.]+)"
        return re.sub(pattern, replace_tag, self.caption)


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
    
    @property
    def processed_caption(self):
        def replace_tag(match):
            username = match.group(1)
            try:
                user = User.objects.get(username=username)
                return f'<a class="user-link" href={reverse('post:detail_profile_view', kwargs={"user_id": user.id})}>@{username}</a>'
            except User.DoesNotExist:
                return f'<a class="user-link" href="#">@{username}</a>' 
            
        pattern = r"@([\w.]+)"
        return re.sub(pattern, replace_tag, self.comment_text)


class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey('account.Profile', related_name='likes', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE, blank=True, null=True)
    like = models.BooleanField(default=False)

    def __str__(self):
        return f'Like: {self.like}'
    

class Follow(models.Model):
    user_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follower', on_delete=models.CASCADE)
    user_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.BooleanField(default=True)


class TagNotification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='tag_notification', on_delete=models.CASCADE)
    last_tagged_at= models.DateTimeField(default=timezone.now)
    notification_last_clicked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - last time tagged: {self.last_tagged_at} - last time tags viewed: {self.notification_last_clicked}'


class UserTagged(models.Model):
    user_tagged = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tagged_user', on_delete=models.CASCADE)
    tagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tagged_by', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='tagged_users', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f'{self.tagged_by.username} tagged {self.user_tagged.username} on post id: {self.post.id}'

class RecentlySearched(models.Model):
    searching_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='searching_user', on_delete=models.CASCADE)
    searched_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='searched_user', on_delete=models.CASCADE)
    last_viewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.searching_user.username} searched for {self.searched_user.username} on {self.last_viewed}'
    
    class Meta:
        ordering = ['-last_viewed']
        constraints = [
            UniqueConstraint(fields=['searching_user', 'searched_user'], name='unique_search')
        ]
    
