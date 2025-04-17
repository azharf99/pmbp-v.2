from django.urls import path
from .views import RenderJsonToView


urlpatterns = [
    path('', RenderJsonToView)
]