from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products import views
from admin_views import admin_dashboard, admin_orders, admin_products, admin_payments, update_order_status, update_payment_status
from auth_views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('products/', views.products_list, name='products_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.user_profile, name='profile'),
    path('payment/<int:order_id>/', views.payment_selection, name='payment_selection'),
    path('payment/<int:order_id>/process/', views.process_payment, name='process_payment'),
    path('payment/<int:order_id>/success/', views.payment_success, name='payment_success'),
    path('payment/<int:order_id>/failed/', views.payment_failed, name='payment_failed'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/cancellation-confirmation/', views.cancellation_confirmation, name='cancellation_confirmation'),
    path('orders/<int:order_id>/refund-status/', views.refund_status, name='refund_status'),
    
    # Password Reset URLs
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Admin URLs
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-orders/', admin_orders, name='admin_orders'),
    path('admin-products/', admin_products, name='admin_products'),
    path('admin-payments/', admin_payments, name='admin_payments'),
    path('admin/orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('admin/payments/<int:payment_id>/update-status/', update_payment_status, name='update_payment_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)