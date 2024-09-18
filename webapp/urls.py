"""
URL configuration for webapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from newapp import views
from account import views

urlpatterns = [
   path('admin/', admin.site.urls),
    #path('newapp/',include('newapp.url')),
    #path('',views.index, name ='index'),
   # path('',include('account.urls')),
    path('',views.Signuppage, name='signup'),
    path('login/',views.loginpage, name='Login'),
    path('chatbot/',views.chatbot, name='chatbot'),
    path('logout/',views.logoutpage, name='logout'),
    
]
