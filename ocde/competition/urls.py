from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('<str:string>/', views.openquestion, name='openquestion'),
    path('saveattempt/<str:string>', views.saveattempt, name='saveattempt')
]