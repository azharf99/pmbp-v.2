from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext as _
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

from utils.models import CleanableFileModel

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'
        db_table = "categories"
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category-list')


class Post(CleanableFileModel):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
    )
    
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique_for_date='created_at', db_index=True)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', db_index=True)
    category = models.ManyToManyField(Category, related_name='posts', db_index=True)
    tags = TaggableManager(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'posts'
        db_table = "posts"
        indexes = [
            models.Index(fields=['slug', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status']),
        ]

    def __str__(self):
        return self.title
    
    file_field_names = ['featured_image']

    def get_absolute_url(self):
        return reverse('blog:post-detail', args=[self.slug])
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    active = models.BooleanField(default=False, db_index=True) #For comments moderation

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'comments'
        db_table = "comments"
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['active', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'