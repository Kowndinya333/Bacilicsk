from os import name
from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('savecode', views.savecode, name="savecode"),
    path('runcode/', views.runcode, name="runcode"),
]