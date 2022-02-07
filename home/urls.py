from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.handleLogin,name='handleLogin'),
    # path('handleSignup', views.handleSignup,name='handleSignup'),
    path('home', views.home,name='home'),
    path('report', views.report,name='report'),
    path('order', views.order,name='order'),
    path('order/invoice/<id>', views.GeneratePdf,name='order-invoice'),
    path('order/cancel/<id>', views.cancelOrder,name='order-cancel'),
    path('product', views.product,name='product'),
    path('product/add', views.addProduct,name='addProduct'),
    path('product/edit/<id>', views.editProduct,name='editProduct'),
    path('product/delete/<id>', views.deleteProduct,name='deleteProduct'),
    path('order-history', views.orderHistory,name='order-history'),
    path('order-history/<str:id>', views.orderHistory,name='order-history'),
    path('getCategoryProductSale', views.getCategoryProductSale,name='getCategoryProductSale'),
    path('getCategorySale', views.getCategorySale,name='getCategorySale'),
    path('getOrderSale', views.getOrderSale,name='getOrderSale'),
    path('getOrderSaleByMonth', views.getOrderSaleByMonth,name='getOrderSaleByMonth'),
    path('expense', views.expense,name='expense'),
    path('expense/add', views.addExpense,name='addExpense'),
    # path('customerExist', views.customerExist,name='customerExist'),
    path('handleLogout', views.handleLogout,name='handleLogout'),
]