"""
URL configuration for webserv project.

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
from django.urls import path
from rate.views import register, login, logout, list_modules, rate_professor, view, average

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/' , register),
    path('api/login/', login),
    path('api/list/', list_modules),
    path('api/rate/', rate_professor),
    path('api/view/', view),
    path('api/average/', average),
    path('api/logout/', logout),
]
