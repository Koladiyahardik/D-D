from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Payment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'final_price', 'stock', 'is_featured', 'is_active', 'created_at')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_featured', 'is_active')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at', 'cancelled_at')
    list_filter = ('status', 'created_at', 'cancelled_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'shipping_name')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'created_at', 'cancelled_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__created_at', 'product__category')
    search_fields = ('order__order_number', 'product__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'payment_status', 'amount', 'refund_status', 'created_at')
    list_filter = ('payment_method', 'payment_status', 'refund_status', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'refund_transaction_id')
    readonly_fields = ('created_at', 'payment_date', 'refund_initiated_at', 'refund_completed_at')
    list_editable = ('payment_status', 'refund_status')