from django.urls import path, include

from utils.title_active_link import set_headtitle_and_active_link
from .views import (
    PostListView,
    PostCreateView,
    PostDetailView,
    CategoryPostsView,
    SignUpView,
)

urlpatterns = [
    path('', PostListView.as_view(), set_headtitle_and_active_link("Blog Post List", "blog"), name='post_list'),
    path('create/', PostCreateView.as_view(), set_headtitle_and_active_link("Blog Post Create", "blog"), name='post_create'),
    path('<slug:slug>/', PostDetailView.as_view(), set_headtitle_and_active_link("Blog Post Detail", "blog"), name='post_detail'),
    path('update/<slug:slug>/', PostDetailView.as_view(), set_headtitle_and_active_link("Blog Post Update", "blog"), name='post_update'),
    path('delete/<slug:slug>/', PostDetailView.as_view(), set_headtitle_and_active_link("Blog Post Delete", "blog"), name='post_delete'),
    path('category/<slug:slug>/', CategoryPostsView.as_view(), set_headtitle_and_active_link("Blog Category", "blog"), name='category'),
    # path('accounts/signup/', SignUpView.as_view(), set_headtitle_and_active_link("Blog Sign Up", "blog"), name='signup'),
    # path('accounts/', include('django.contrib.auth.urls'), set_headtitle_and_active_link("Blog Accounts", "blog"), name='accounts'),
]