from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('investments/', views.investment_view, name="investments"),
    path('add-asset/', views.add_asset, name="add_asset"),
    path('remove-asset/', views.delete_asset, name="delete_asset"),
]
