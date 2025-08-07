from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-account/', views.verify_account, name='verify_account'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset-link/', views.verify_password_reset_link, name='password_reset_confirm'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
]