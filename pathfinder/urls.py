from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('compute_path/', views.compute_path, name="compute_path"),
]
