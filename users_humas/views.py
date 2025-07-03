from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.core.cache import cache
from django.forms import BaseModelForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from userlog.models import UserLog
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.db.models.query import QuerySet
from django.contrib import messages
from django.template.response import TemplateResponse
from users.models import Teacher
from users.forms import ProfileUpdateForm, UserCreateForm, UserUpdateForm, UserPasswordUpdateForm
from utils.whatsapp_albinaa import send_WA_general, send_WA_create_update_delete
from typing import Any

# Create your views here.
class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        cache.clear()
        return super().get(request, *args, **kwargs)
    
    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))
    
    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        if self.request.POST.get("remember"):
            self.request.session.set_expiry(1209600)
        else:
           self.request.session.set_expiry(0)

        UserLog.objects.create(
                user=form.get_user().teacher,
                action_flag="LOGIN",
                app="USERS",
                message="berhasil melakukan login ke aplikasi"
            )
        send_WA_general(form.get_user().teacher.no_hp, 'login', 'Selamat datang di Aplikasi Humas & PT')
        messages.success(self.request, "Login Berhasil! :)")
        return super().form_valid(form)


class MyProfileView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = "registration/profile.html"
    
    def get_queryset(self) -> QuerySet[Any]:
        return get_object_or_404(Teacher, user_id=self.request.user.id)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['name'] = "Overview"
        return context

class MyProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = ProfileUpdateForm
    template_name = "registration/profile_form.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id == self.kwargs.get("pk") or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="PROFILE",
                message=f"berhasil melakukan update profil {self.obj}"
            )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'update', f'data profil {self.obj}', 'accounts/', 'profile/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['teacher'] = self.get_queryset()
        context['name'] = "Edit Profile"
        return context

class MyLogoutView(LogoutView):

    def post(self, request: WSGIRequest, *args: Any, **kwargs: Any) -> TemplateResponse:
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="LOGOUT",
            app="USERS",
            message="berhasil logout dari aplikasi",
        )
        send_WA_general(request.user.teacher.no_hp, 'logout', 'Selamat jalan!')
        messages.success(self.request, "Selamat Jalan, Logout Berhasil! :)")
        cache.clear()
        return super().post(request, *args, **kwargs)
    

class UserListView(LoginRequiredMixin, ListView):
    model = User


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy("user-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Input Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="USERS",
            message=f"berhasil menambahkan data user {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'menambahkan', f'data user {self.obj}', 'accounts/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.id == self.kwargs.get("pk") or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy("user-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.id == self.kwargs.get("pk") or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="USERS",
            message=f"berhasil update data user {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'update', f'data user {self.obj}', 'accounts/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Update"
        return c
    

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("user-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="USERS",
            message=f"berhasil menghapus data user {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'menghapus', f'data user {self.obj}', 'accounts/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordUpdateForm
    success_url = reverse_lazy("user-change-password-done")

    def get_object(self):
        # Get the user object based on the pk from the URL
        return get_object_or_404(User, pk=self.kwargs.get("pk"))
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Bind the form to the correct user instance
        kwargs['user'] = self.get_object()
        return kwargs
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.id == self.kwargs.get("pk") or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Password Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="USERS",
            message=f"berhasil mengubah password user {self.object}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'mengubah', f'password user {self.object}', 'accounts/', 'profile/')
        messages.success(self.request, "Update Password Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name ="registration/password_change_done.html"
    

class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher


class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("teacher-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Input Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="TEACHER",
            message=f"berhasil menambahkan data guru {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'menambahkan', f'data guru {self.obj}', 'accounts/', 'teachers/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c


class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("teacher-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id == self.kwargs.get("pk") or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="TEACHER",
            message=f"berhasil update data guru {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'update', f'data guru {self.obj}', 'accounts/', 'teachers/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Update"
        return c
    

class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    success_url = reverse_lazy("teacher-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="TEACHER",
            message=f"berhasil menghapus data guru {self.obj}",
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'menghapus', f'data guru {self.obj}', 'accounts/', 'teachers/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)