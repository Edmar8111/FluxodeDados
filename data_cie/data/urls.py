from django.urls import path
from . import views


urlpatterns = [
    path('home', views.home0, name='home0'),
    path('grafico', views.grafico, name='grafico')
]