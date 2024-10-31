from django.forms import ModelForm
from . models import Post, Comment

class PostCreateForm(ModelForm):
    class Meta:
        model = Post
        fields = ['photo', 'caption']

class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
    