from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('post-create/', views.post_create, name='post_create'),
    path('feed/', views.feed, name='feed'),
    path('my-profile/', views.my_profile_view, name='my_profile'),
    path('profile/<int:user_id>/', views.detail_profile_view, name='detail_profile_view'),
    path('follow-unfollow-user/<int:user_id>/<int:other_user_id>/', views.follow_unfollow_user, name='follow_unfollow_user'),
    path('followers-following-view/<int:user_id>/<str:flag>/', views.followers_following_view, name='followers_following_view'),
    path('my-messages/<int:user_id>/', views.messages_view, name='messages_view'),
    path('post-detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post-comment-add/<int:post_id>/', views.post_comment_add, name='post_comment_add'),
    path('post-like/<int:post_id>/', views.post_like, name='post_like'),
    path('comment-like/<int:post_id>/<int:comment_id>/', views.comment_like, name='comment_like'),
    path('comment-reply/<int:post_id>/<int:comment_id>/', views.comment_reply, name='comment_reply'),
    path('comment-replies-view/<int:post_id>/<int:comment_id>/', views.comment_replies_view, name='comment_replies_view'),
]