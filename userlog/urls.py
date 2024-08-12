from django.urls import path
from userlog.views import UserLogListView, UserLogCreateView, UserLogDetailView, UserLogUpdateView, UserLogDeleteView

urlpatterns = [
    path("", UserLogListView.as_view(), name="userlog-list"),
    path("create/", UserLogCreateView.as_view(), name="userlog-create"),
    path("detail/<int:pk>/", UserLogDetailView.as_view(), name="userlog-detail"),
    path("update/<int:pk>/", UserLogUpdateView.as_view(), name="userlog-update"),
    path("delete/<int:pk>/", UserLogDeleteView.as_view(), name="userlog-delete"),
]