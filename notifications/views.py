# views.py
from typing import Any
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import Notification

class NotificationIndexView(ListView):
    model = Notification

class NotificationDetailView(DetailView):
    model = Notification

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        obj = self.get_object()
        if obj.teacher == request.user.teacher:
            obj.is_read=True
            obj.save()
        else:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

class NotificationCreateView(CreateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')

class NotificationQuickCreateView(CreateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')

class NotificationUpdateView(UpdateView):
    model = Notification
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('notification-list')
    
class NotificationDeleteView(DeleteView):
    model = Notification
    success_url = reverse_lazy('notification-list')