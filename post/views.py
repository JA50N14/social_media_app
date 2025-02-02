from django.shortcuts import render, redirect, get_object_or_404
from . models import Post, Like, Comment, Follow, TagNotification, UserTagged
from chat.models import Chat, Message, ChatViewed
from account.models import Profile
from . forms import PostCreateForm, CommentCreateForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q, F, Subquery, Case, When
from django.db.models.functions import Substr
from django.utils import timezone
import re

# Create your views here.

#Work on the notifications.html - You need to bold links that have not been clicked and unbold links that have been clicked.

def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            update_tag_notification_model(post, request.user)
            return redirect('post:my_profile')
    else:
        form = PostCreateForm()
    return render(request, 'post/post_create.html', {'form': form})


def post_detail(request, post_id, user_tagged_id=None):
    post = get_object_or_404(Post, pk=post_id)
    user = post.user
    user_like_post = post.likes.filter(user=request.user).first()
    if user_like_post and user_like_post.like:
        post_like_status = True
    else:
        post_like_status = False
    comments = post.comments.filter(parent_comment=None).order_by('-created')[:10]
    for comment in comments:
        comment.user_liked = comment.likes.filter(user=request.user, like=True).exists()
    if user_tagged_id:
        UserTagged.objects.filter(id=user_tagged_id).update(seen=True) 

    return render(request, 'post/post_detail.html', {'post': post, 'user': user, 'comments': comments, 'post_like_status': post_like_status})


def post_comment_add(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            update_tag_notification_model(post, request.user, comment)
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
    
    if user_like_post.like:
        post_like_status = True
    else:
        post_like_status = False

    return render(request, 'partials/post_like.html', {'post': post, 'post_like_status': post_like_status})


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
            update_tag_notification_model(post, request.user, comment_reply)
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
    user = request.user
    all_posts = Post.objects.filter(user=user).order_by("-created")
    paginator = Paginator(all_posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    post_count = all_posts.count()
    follower_count = Follow.objects.filter(user_to=user).count()
    following_count = Follow.objects.filter(user_from=user).count()
    return render(request, 'post/my_profile.html', {'page_obj': page_obj, 'profile': profile, 'post_count': post_count, 'follower_count': follower_count, 'following_count': following_count})


def detail_profile_view(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user_likes_sq = Like.objects.filter(post=OuterRef('pk'), user=request.user, like=True)
    all_posts = Post.objects.filter(user=user).order_by("-created").annotate(post_like_status=Exists(user_likes_sq))
    paginator = Paginator(all_posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None
    post_count = all_posts.count()
    follower_count = Follow.objects.filter(user_to=user, following=True).count()
    following_count = Follow.objects.filter(user_from=user, following=True).count()
    following_user = Follow.objects.filter(user_from=request.user, user_to=user).first()
    return render(request, 'post/detail_profile.html', {'user': user, 'page_obj': page_obj, 'profile': profile, 'post_count': post_count, 'follower_count': follower_count, 'following_count': following_count, 'following_user': following_user})


def follow_unfollow_user(request, user_id, other_user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    other_user = get_object_or_404(User, id=other_user_id)
    following_user = Follow.objects.filter(user_from=user, user_to=other_user).first()
    if not following_user:
        following_user = Follow.objects.create(user_from=user, user_to=other_user, following=True)
    else:
        following_user.following = not following_user.following
        following_user.save()
    follower_count = Follow.objects.filter(user_to=other_user, following=True).count()
    return render(request, 'partials/following.html', {'user_id': user_id, 'other_user_id': other_user_id, 'following_user': following_user, 'follower_count': follower_count})


def followers_following_view(request, user_id, flag):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    if flag == 'followers':
        followers = Follow.objects.filter(user_to=user)
        follower_count = followers.count()
        following_count = Follow.objects.filter(user_from=user).count()
        return render(request, 'post/followers_following.html', {'user': user, 'followers': followers, 'follower_count': follower_count, 'following_count': following_count, 'flag': flag})
    else:
        following = Follow.objects.filter(user_from=user)
        following_count = following.count()
        follower_count = Follow.objects.filter(user_to=user).count()
        return render(request, 'post/followers_following.html', {'user': user, 'following': following, 'follower_count': follower_count, 'following_count': following_count, 'flag': flag})


def messages_view(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    messages_exists_sq = Message.objects.filter(chat=OuterRef('pk'))
    latest_message_sq = Message.objects.filter(chat=OuterRef('pk')).values_list('content', flat=True)[:1]
    latest_message_time_sq = Message.objects.filter(chat=OuterRef('pk')).values_list('timestamp', flat=True)[:1]
    
    latest_message_seen_sq = Message.objects.filter(chat=OuterRef('pk')).exclude(sender=user).filter(timestamp__gt=ChatViewed.objects.filter(chat=OuterRef('chat'), user=user).values('last_viewed')[:1])
    #The issue was the OuterRef('pk') referencing the 'pk' of the Message instance, not the 'pk' of the Chat instance. Once I changed the OuterRef to chat (i.e."chat=OuterRef('chat')"), it is now referencing the Chat instnace associated with the Message instance.

    chat_with_user1_id_sq = User.objects.filter(pk=OuterRef('user2')).values('id')[:1]
    chat_with_user2_id_sq = User.objects.filter(pk=OuterRef('user1')).values('id')[:1]

    chat_with_user1_first_name_sq = User.objects.filter(pk=OuterRef('user2')).values('first_name')[:1]
    chat_with_user2_first_name_sq = User.objects.filter(pk=OuterRef('user1')).values('first_name')[:1]

    chat_with_user1_last_name_sq = User.objects.filter(pk=OuterRef('user2')).values('last_name')[:1]
    chat_with_user2_last_name_sq = User.objects.filter(pk=OuterRef('user1')).values('last_name')[:1]

    user_chats = Chat.objects.filter(Q(user1=user)|Q(user2=user), Exists(messages_exists_sq)).annotate(latest_message=Substr(Subquery(latest_message_sq), 1, 25), latest_message_time=Subquery(latest_message_time_sq), chat_with_id=Case(When(user1=user, then=Subquery(chat_with_user1_id_sq)), When(user2=user, then=Subquery(chat_with_user2_id_sq))), chat_with_first_name=Case(When(user1=user, then=Subquery(chat_with_user1_first_name_sq)), When(user2=user, then=Subquery(chat_with_user2_first_name_sq))), chat_with_last_name=Case(When(user1=user, then=Subquery(chat_with_user1_last_name_sq)), When(user2=user, then=Subquery(chat_with_user2_last_name_sq))), is_new=Exists(Subquery(latest_message_seen_sq))).order_by('-latest_message_time')

    return render(request, 'post/messages.html', {'user_chats': user_chats})


def feed(request):
    user=request.user
    following_users = Follow.objects.filter(user_from=user, following=True).values_list('user_to', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by("-created")
    if not posts.exists():
        posts = Post.objects.all().exclude(user=user).order_by("-created")

    posts.annotate(post_like_status=Exists(Like.objects.filter(post=OuterRef('pk'), user=user, like=True)))

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'post/feed.html', {'page_obj': page_obj})


def notifications_view(request, user_id):
    user = User.objects.get(id=user_id)
    TagNotification.objects.update_or_create(user=user, defaults={'notification_last_clicked': timezone.now})
    tags = UserTagged.objects.filter(user_tagged=user)
    for tag in tags:
        print(tag.seen)
    paginator = Paginator(tags, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'post/notifications.html', {'page_obj': page_obj})


def update_tag_notification_model(post, post_user, comment=None):
    pattern = r"@([\w.]+)"
    if comment == None:
        username_lst = re.findall(pattern, post.caption)
    else:
        username_lst = re.findall(pattern, comment.comment_text)
    tagged_users = User.objects.filter(username__in=username_lst)
    for tagged_user in tagged_users:
        TagNotification.objects.update_or_create(user=tagged_user, defaults={'last_tagged_at': timezone.now})
        
        create_user_tagged_instance(tagged_user, post, post_user)


def create_user_tagged_instance(tagged_user, post, post_user):
    UserTagged.objects.create(user_tagged=tagged_user, tagged_by=post_user, post=post)


def check_for_new_notifications(request, user_id):
    user = get_object_or_404(User, id=user_id)
    tag_notification = TagNotification.objects.get(user=user)
    if tag_notification.last_tagged_at > tag_notification.notification_last_clicked:
        data = {'new_tag': True}
        print(f'{user.username} - New Post')
    else:
        data = {'new_tag': False}
        print(f'{user.username} - No New Post')
    return JsonResponse(data)


def autocomplete_user_tags(request):
    user_string = request.GET.get('q')
    if user_string.startswith('@'):
        user_string = user_string[1:]

    if user_string:
        user_list = User.objects.filter(username__startswith=user_string)[:10].values_list('username', flat=True)
        return JsonResponse({"usernames": user_list})
    
    return JsonResponse({"usernames": []})


#Create auto-complete feature. 



