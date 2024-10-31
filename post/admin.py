from django.contrib import admin
from .models import Post, Comment
from django.utils.html import format_html

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'created', 'display_photo')
    search_fields = ('caption',)
    list_filters = ('user', 'created')

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50")/>', obj.photo.url)
        return "No Photo"
    
