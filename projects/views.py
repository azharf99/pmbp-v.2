
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from projects.models import Team, Project, DailyPlan
from projects.forms import TeamForm, ProjectForm, DailyPlanForm
from utils.whatsapp import send_WA_daily_plan

# Create your views here.
class TeamIndexView(ListView):
    model = Team
    

class TeamDetailView(DetailView):
    model = Team


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy("team-list")
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
    

class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy("team-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    success_url = reverse_lazy("team-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


class ProjectIndexView(ListView):
    model = Project
    

class ProjectDetailView(DetailView):
    model = Project


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("project-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
    

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy("project-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy("project-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)



class DailyPlanIndexView(ListView):
    model = DailyPlan
    

class DailyPlanDetailView(DetailView):
    model = DailyPlan


class DailyPlanCreateView(CreateView):
    model = DailyPlan
    form_class = DailyPlanForm
    success_url = reverse_lazy("daily-plan-list")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        send_WA_daily_plan(self.object.project.teacher.phone, f"{self.object}", f"{self.object.target_today}", f"{self.object.problems}", self.object.id)
        return HttpResponseRedirect(self.get_success_url())
    

class DailyPlanUpdateView(UpdateView):
    model = DailyPlan
    form_class = DailyPlanForm
    success_url = reverse_lazy("daily-plan-list")


class DailyPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyPlan
    success_url = reverse_lazy("daily-plan-list")


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
    