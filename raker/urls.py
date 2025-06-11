from django.urls import path
from raker.views import LaporanPertanggungJawabanCreateView, LaporanPertanggungJawabanUpdateView, LaporanPertanggungJawabanDeleteView
from utils.views import LPJPMBPView

urlpatterns = [
    path('', LPJPMBPView.as_view(), name='lpj'),
    path("create/", LaporanPertanggungJawabanCreateView.as_view(), name="lpj-create"),
    path("update/<int:pk>/", LaporanPertanggungJawabanUpdateView.as_view(), name="lpj-update"),
    path("delete/<int:pk>/", LaporanPertanggungJawabanDeleteView.as_view(), name="lpj-delete"),
]