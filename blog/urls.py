from django.urls import path
from utils.title_active_link import set_headtitle_and_active_link
from .views import (
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostDetailView,
    CategoryPostsView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    CategoryPostsDetailView,
)

urlpatterns = [
    path('', PostListView.as_view(), set_headtitle_and_active_link("Blog Post List", "blog"), name='post-list'),
    path('create/', PostCreateView.as_view(), set_headtitle_and_active_link("Blog Post Create", "blog"), name='post-create'),
    path('detail/<slug:slug>/', PostDetailView.as_view(), set_headtitle_and_active_link("Blog Post Detail", "blog"), name='post-detail'),
    path('update/<slug:slug>/', PostUpdateView.as_view(), set_headtitle_and_active_link("Blog Post Update", "blog"), name='post-update'),
    path('delete/<slug:slug>/', PostDeleteView.as_view(), set_headtitle_and_active_link("Blog Post Delete", "blog"), name='post-delete'),
    path('category/', CategoryPostsView.as_view(), set_headtitle_and_active_link("Blog Category", "blog"), name='category-list'),
    path('category/create/', CategoryCreateView.as_view(), set_headtitle_and_active_link("Blog Category Create", "blog"), name='category-create'),
    path('category/<slug:slug>/', CategoryPostsDetailView.as_view(), set_headtitle_and_active_link("Blog Category", "blog"), name='category-detail'),
    path('category/update/<slug:slug>/', CategoryUpdateView.as_view(), set_headtitle_and_active_link("Blog Category Update", "blog"), name='category-update'),
    path('category/delete/<slug:slug>/', CategoryDeleteView.as_view(), set_headtitle_and_active_link("Blog Category Delete", "blog"), name='category-delete'),
]