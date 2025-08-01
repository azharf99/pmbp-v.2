
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from projects.models import Team, Project, DailyPlan
from projects.forms import TeamForm, ProjectForm, DailyPlanForm

# Create your views here.
class TeamIndexView(ListView):
    model = Team
    

class TeamDetailView(DetailView):
    model = Team


class TeamCreateView(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Team
    form_class = TeamForm
    permission_required = "projects.add_team"
    success_url = reverse_lazy("team-list")
    

class TeamUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    permission_required = "projects.change_team"
    success_url = reverse_lazy("team-list")


class TeamDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Team
    permission_required = "projects.delete_team"
    success_url = reverse_lazy("team-list")


class ProjectIndexView(ListView):
    model = Project
    

class ProjectDetailView(DetailView):
    model = Project


class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    permission_required = "projects.add_project"
    success_url = reverse_lazy("project-list")
    

class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    permission_required = "projects.change_project"
    success_url = reverse_lazy("project-list")


class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Project
    permission_required = "projects.delete_project"
    success_url = reverse_lazy("project-list")



class DailyPlanIndexView(ListView):
    model = DailyPlan
    

class DailyPlanDetailView(DetailView):
    model = DailyPlan


class DailyPlanCreateView(CreateView):
    model = DailyPlan
    form_class = DailyPlanForm
    success_url = reverse_lazy("daily-plan-list")

class DailyPlanUpdateView(UpdateView):
    model = DailyPlan
    form_class = DailyPlanForm
    success_url = reverse_lazy("daily-plan-list")


class DailyPlanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = DailyPlan
    permission_required = "projects.delete_dailyplan"
    success_url = reverse_lazy("daily-plan-list")