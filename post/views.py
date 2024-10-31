from django.shortcuts import render, redirect, get_object_or_404
from . models import Post, Like, Comment, Follow
from . forms import PostCreateForm, CommentCreateForm
from django.http import HttpResponse

# Create your views here.

def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('post:my_profile', request.user.id)
    else:
        form = PostCreateForm()
    return render(request, 'post/post_create.html', {'form': form})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user_like_post = post.likes.filter(user=request.user).first()
    comments = post.comments.filter(parent_comment=None).order_by('-created')[:10]
    for comment in comments:
        comment.user_liked = comment.likes.filter(user=request.user, like=True).exists()
    return render(request, 'post/post_detail.html', {'post': post, 'comments': comments, 'user_like_post':user_like_post})


def post_comment_add(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return render(request, 'partials/comment.html', {'comment': comment})
    else:
        form = CommentCreateForm()
    return render(request, 'partials/comment_form.html', {'form': form, 'post_id': post_id})


def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_like_post = post.likes.filter(user=request.user).first()

    if not user_like_post:
        user_like_post = Like.objects.create(post=post, user=request.user, like=True)
    else:
        user_like_post.like = not user_like_post.like
        user_like_post.save()

    return render(request, 'partials/post_like.html', {'post': post, 'user_like_post': user_like_post})


def comment_like(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    user_like_comment = comment.likes.filter(user=request.user).first()
    if not user_like_comment:
        user_like_comment = Like.objects.create(user=request.user, comment=comment, like=True)
    else:
        user_like_comment.like = not user_like_comment.like
        user_like_comment.save()
    comment.user_liked = comment.likes.filter(user=request.user, like=True).exists()
    return render(request, 'partials/comment_like.html', {'post': post, 'comment': comment})


def comment_reply(request, post_id, comment_id):
    if request.method == 'POST':
        comment_reply_form = CommentCreateForm(request.POST)
        if comment_reply_form.is_valid():
            comment_reply = comment_reply_form.save(commit=False)
            post = get_object_or_404(Post, id=post_id)
            parent_comment = get_object_or_404(Comment, id=comment_id)
            comment_reply.user, comment_reply.post, comment_reply.parent_comment = request.user, post, parent_comment
            comment_reply.save()
            all_comment_replies = parent_comment.get_all_replies()
            return render(request, 'partials/comment_replies.html', {'post': post, 'all_comment_replies': all_comment_replies})
    else:
        comment_reply_form = CommentCreateForm()
    return render(request, 'partials/comment_reply_form.html', {'post_id': post_id, 'comment_id': comment_id, 'comment_reply_form': comment_reply_form})


def comment_replies_view(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)
    all_comment_replies = comment.get_all_replies()
    for reply in all_comment_replies:
        reply.user_liked = reply.likes.filter(user=request.user, like=True).exists()
    return render(request, 'partials/comment_replies.html', {'post': post, 'all_comment_replies': all_comment_replies})



def my_profile_view(request):
    all_posts = Post.objects.filter(user=request.user)
    post_count = Post.objects.filter(user=request.user).count()
    follower_count = Follow.objects.filter(user_to=request.user).count()
    following_count = Follow.objects.filter(user_from=request.user).count()
    return render(request, 'post/my_profile.html', {'all_posts': all_posts, 'post_count': post_count, 'follower_count': follower_count, 'following_count': following_count})

def my_followers_view(self):
    pass


def feed(request):
    if request.method == 'GET':
        return render(request, 'post/feed.html')

