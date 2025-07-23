# views.py
from typing import Any
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import Notification

class NotificationIndexView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Notification
    permission_required = 'notifications.view_notification'
    
    

class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        obj = self.get_object()
        if obj.teacher == request.user.teacher:
            obj.is_read=True
            obj.save()
        else:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

class NotificationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')
    permission_required = 'notifications.add_notification'

class NotificationQuickCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')
    permission_required = 'notifications.add_notification'

class NotificationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')
    permission_required = 'notifications.change_notification'
    
class NotificationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy('notification-list')
    permission_required = 'notifications.delete_notification'