from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name="password_change"),
    path('password-change/complete/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-profile-bio/', views.edit_profile_bio, name='edit_profile_bio'),
    path('edit-profile-profile-photo/', views.edit_profile_photo, name="edit_profile_photo"),
    path('edit-first-last-name/', views.edit_first_last_name, name="edit_first_last_name"),
    path('edit-date-of-birth/', views.edit_date_of_birth, name='edit_date_of_birth'),
    path('edit-username/', views.edit_username, name='edit_username'),
]