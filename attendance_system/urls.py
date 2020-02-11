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
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework.routers import DefaultRouter

from users.views import UsersViewset, UserViewset, VerifyCodeViewset, ChangePasswordViewset
from users.views import getUserFuzzyMailViewset, checkUserMailViewset, sendOldMailCaptchaViewset, confirmOldMailCaptchaViewset, sendNewMailCaptchaViewset, confirmNewMailCaptchaViewset
from users.views import delMultipleUserViewset

router = DefaultRouter()
# router.register(r'users', UsersViewset, basename="users")
router.register(r'code', VerifyCodeViewset, basename="code")
# router.register(r'changepassword', ChangePasswordViewset, basename="changepassword")

router.register(r'member/security/getUserFuzzyMail', getUserFuzzyMailViewset, basename="getUserFuzzyMail")
router.register(r'member/security/checkUserMail', checkUserMailViewset, basename="checkUserMail")
router.register(r'member/security/sendOldMailCaptcha', sendOldMailCaptchaViewset, basename="sendOldMailCaptcha")
router.register(r'member/security/confirmOldMailCaptcha', confirmOldMailCaptchaViewset, basename="confirmOldMailCaptcha")
router.register(r'member/security/sendNewMailCaptcha', sendNewMailCaptchaViewset, basename="sendNewMailCaptcha")
router.register(r'member/security/confirmNewMailCaptcha', confirmNewMailCaptchaViewset, basename="confirmNewMailCaptcha")

router.register(r'users', UserViewset, basename="user")

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),

    # jwt的认证接口
    url(r'^login/', obtain_jwt_token),
    url(r'^token-verify/', verify_jwt_token)
]
