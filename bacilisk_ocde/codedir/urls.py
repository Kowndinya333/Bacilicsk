from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('parse/', views.parsepath, name='parsepath'),
    path('newfolder/', views.newfolder, name='newfolder'),
    path('newfile/', views.newfile, name='newfile'),
    path('deletefolder', views.deletefolder, name='deletefolder'),
    path('deletefile', views.deletefile, name='deletefile'),
]  
