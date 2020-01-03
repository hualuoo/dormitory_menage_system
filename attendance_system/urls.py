"""attendance_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from users.views import UserViewset, UserInfoViewset, VerifyCodeViewset


router = DefaultRouter()
router.register(r'users', UserViewset, basename="users")
router.register(r'userinfo', UserInfoViewset, basename="userinfo")
router.register(r'code', VerifyCodeViewset, basename="code")

urlpatterns = [
    path('admin/', admin.site.urls),

    #url(r'users/$', UsersListView.as_view(), name="users-list"),

    url(r'^', include(router.urls)),

    # jwt的认证接口
    url(r'^jwt_login/', obtain_jwt_token),
]
