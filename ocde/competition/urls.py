from os import name
from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('open/<str:string>/', views.openquestion, name='openquestion'),
    path('saveattempt/<str:string>', views.saveattempt, name='saveattempt'),
    path('runcode/<str:string>', views.runcode, name='runcode'),
    path('validate/<str:string>', views.validate, name="validate"),
    path('results/', views.results, name='results'),
]