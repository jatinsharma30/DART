from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.handleLogin,name='handleLogin'),
    path('handleSignup', views.handleSignup,name='handleSignup'),
    path('home', views.home,name='home'),
    path('report', views.report,name='report'),
    path('order', views.order,name='order'),
    path('product', views.product,name='product'),
    path('order-history', views.orderHistory,name='order-history'),
    path('getProductsSale', views.getProductsSale,name='getProductsSale'),
    path('getOrderSale', views.getOrderSale,name='getOrderSale'),
    path('handleLogout', views.handleLogout,name='handleLogout'),
]