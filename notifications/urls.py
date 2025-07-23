from django.urls import path

from notifications.views import NotificationCreateView, NotificationDeleteView, NotificationDetailView, NotificationIndexView, NotificationQuickCreateView, NotificationUpdateView

urlpatterns = [
    path('', NotificationIndexView.as_view(), name='notification-list'),
    path('create/', NotificationCreateView.as_view(), name='notification-create'),
    path('quick-create/', NotificationQuickCreateView.as_view(), name='notification-quick-create'),
    path('detail/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('update/<int:pk>/', NotificationUpdateView.as_view(), name='notification-update'),
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
]