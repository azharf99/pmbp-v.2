from django.contrib import admin
from .models import Post, Comment, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'author', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('author__username', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)