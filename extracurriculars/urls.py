from django.urls import path
from extracurriculars.views import ExtracurricularIndexView, ExtracurricularCreateView, ExtracurricularDetailView,\
                                    ExtracurricularUpdateView, ExtracurricularDeleteView, ExtracurricularGetMembersView


urlpatterns = [
    path('', ExtracurricularIndexView.as_view(), name='extracurricular-list'),
    path('create/', ExtracurricularCreateView.as_view(), name='extracurricular-create'),
    path('get-members/', ExtracurricularGetMembersView.as_view(), name='extracurricular-get-members'),
    path('detail/<slug:slug>/', ExtracurricularDetailView.as_view(), name='extracurricular-detail'),
    path('update/<slug:slug>/', ExtracurricularUpdateView.as_view(), name='extracurricular-update'),
    path('delete/<slug:slug>/', ExtracurricularDeleteView.as_view(), name='extracurricular-delete'),
]