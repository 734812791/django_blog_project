from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from .views import user_list, SignUpSuccessView, SignUpView, UpdateUser, change_password, ChangePasswordFail, \
    ChangePasswordSuccess

app_name = 'user'

urlpatterns = [
    path('user_list/', user_list, name='user_list'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup_success/', SignUpSuccessView.as_view(), name='signup_success'),
    path('update_user/<str:pk>/', UpdateUser.as_view(), name='update_user'),
    path('change_password/', change_password, name='change_password'),
    path('change_password_fail/', ChangePasswordFail.as_view(), name='change_password_fail'),
    path('change_password_success/', ChangePasswordSuccess.as_view(), name='change_password_success'),
]
