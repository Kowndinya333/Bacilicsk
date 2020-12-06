from django.urls import path

from . import views

urlpatterns=[
    path('mycodes/', views.showcodes, name="showcodes"),
    path('practice/', views.practice, name="practice"),
    path('savecode/', views.savecode, name='savecode'),
    path('showcode/<str:file>', views.showcode, name='showcode'),
    path('deletecode/<str:file>', views.deletecode, name='deletecode'),
    path('updatecode/<str:file>', views.updatecode, name='updatecode'),
    path('runcode/<str:file>', views.runcode, name='runcode'),
]