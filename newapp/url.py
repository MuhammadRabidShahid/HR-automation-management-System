from django.urls import path
from . import views
urlpatterns=[
    path('db/',views.index, name='index')
]