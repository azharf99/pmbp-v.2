from django.urls import path
from nilai.views import NilaiDetailView, NilaiIndexView, PrintExcelView, NilaiCreateView, NilaiUpdateView, NilaiDeleteView

urlpatterns = [
    path('', NilaiIndexView.as_view(), name='nilai-list'),
    path('create/', NilaiCreateView.as_view(), name='nilai-create'),
    path('detail/<int:pk>/', NilaiDetailView.as_view(), name='nilai-detail'),
    path('update/<int:pk>/', NilaiUpdateView.as_view(), name='nilai-update'),
    path('delete/<int:pk>/', NilaiDeleteView.as_view(), name='nilai-delete'),

    path('download/', PrintExcelView.as_view(), name='nilai-download'),
]