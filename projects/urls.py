from django.urls import path
from .views import TeamIndexView, TeamCreateView, TeamDetailView, TeamUpdateView, TeamDeleteView,\
                    ProjectIndexView, ProjectCreateView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView,\
                    DailyPlanIndexView, DailyPlanCreateView, DailyPlanDetailView, DailyPlanUpdateView, DailyPlanDeleteView


urlpatterns = [
    path('', ProjectIndexView.as_view(), name='project-list'),
    path('create', ProjectCreateView.as_view(), name='project-create'),
    path('detail/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('update/<int:pk>/', ProjectUpdateView.as_view(), name='project-update'),
    path('delete/<int:pk>/', ProjectDeleteView.as_view(), name='project-delete'),

    path('team/', TeamIndexView.as_view(), name='team-list'),
    path('team/create', TeamCreateView.as_view(), name='team-create'),
    path('team/detail/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('team/update/<int:pk>/', TeamUpdateView.as_view(), name='team-update'),
    path('team/delete/<int:pk>/', TeamDeleteView.as_view(), name='team-delete'),

    path('plan/', DailyPlanIndexView.as_view(), name='daily-plan-list'),
    path('plan/create', DailyPlanCreateView.as_view(), name='daily-plan-create'),
    path('plan/detail/<int:pk>/', DailyPlanDetailView.as_view(), name='daily-plan-detail'),
    path('plan/update/<int:pk>/', DailyPlanUpdateView.as_view(), name='daily-plan-update'),
    path('plan/delete/<int:pk>/', DailyPlanDeleteView.as_view(), name='daily-plan-delete'),


    # path('<slug:slug>/print', PrintKSMReport.as_view(), name='laporan-ksm-print'),
]