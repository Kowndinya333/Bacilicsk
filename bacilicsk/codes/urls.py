from django.urls import path

from . import views

urlpatterns=[
    path('', views.index, name="index"),
    path('savecode/',views.save_code, name="codesave"),
    path('mycodes/', views.view_codes, name="mycodes"),
    path('<str:file>', views.show_file, name="show_file"),
]