from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:product_id>/', views.CheckOut, name='checkout'),
    path('produtos/', views.ProductView, name='products'),
    path('payment-success/<int:product_id>/<int:usuario_id>/', views.PaymentSuccessful, name='payment-success'),
    path('payment-failed/<int:product_id>//<int:usuario_id>/', views.paymentFailed, name='payment-failed'),
]