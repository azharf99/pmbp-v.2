from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.dates import DayArchiveView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from utils.title_active_link import set_headtitle_and_active_link
from .models import Post, Category, Comment
from .forms import CategoryForm, CommentForm, PostForm
from django.urls import reverse_lazy

class PostListView(ListView):
    model = Post
    template_name = 'blog/post-list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        return context
    

class PostDayArchiveView(DayArchiveView):
    queryset = Post.objects.all()
    date_field = "created_at"
    allow_future = True

class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    form_class = PostForm
    form_name = 'Post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context.update({'form_name': self.form_name})
        return context
    
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    form_name = 'Post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context.update({'form_name': self.form_name})
        return context
    
class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('post-list')
    form_name = 'Post'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context.update({'form_name': self.form_name})
        return context
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post-detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = self.object
            new_comment.author = request.user.teacher
            new_comment.save()
            return redirect(self.object.get_absolute_url())
        
        context = self.get_context_data()
        context['comment_form'] = comment_form
        return self.render_to_response(context)

class CategoryPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class CategoryPostsDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            categories=self.category,
            status='published'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
    
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'pages/form.html'
    form_class = CategoryForm
    form_name = 'Category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context.update({'form_name': self.form_name})
        return context

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'pages/form.html'
    form_class = CategoryForm
    form_name = 'Category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs)
        context.update({'form_name': self.form_name})
        return context

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'pages/delete.html'
    success_url = reverse_lazy('category-list')
