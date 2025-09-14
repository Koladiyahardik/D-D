from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Category, Product, Order, OrderItem, Payment, Cart


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with statistics and quick actions"""
    
    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Payment_Pending').count()
    confirmed_orders = Order.objects.filter(status='Confirmed').count()
    processing_orders = Order.objects.filter(status='Processing').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()
    delivered_orders = Order.objects.filter(status='Delivered').count()
    cancelled_orders = Order.objects.filter(status='Cancelled').count()
    
    # Recent orders (last 7 days)
    recent_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(status__in=['Paid', 'Confirmed', 'Processing', 'Shipped', 'Delivered']).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    monthly_revenue = Order.objects.filter(
        created_at__date__gte=month_ago,
        status__in=['Paid', 'Confirmed', 'Processing', 'Shipped', 'Delivered']
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Product statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    featured_products = Product.objects.filter(is_featured=True).count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    
    # Category statistics
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    
    # Payment statistics
    cod_orders = Payment.objects.filter(payment_method='COD').count()
    online_payments = Payment.objects.filter(payment_method__in=['UPI', 'CARD', 'NETBANKING']).count()
    pending_refunds = Payment.objects.filter(refund_status='Pending').count()
    
    # Recent orders for display
    recent_orders_list = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Top selling products
    top_products = OrderItem.objects.values('product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # User statistics
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    recent_users = User.objects.filter(date_joined__date__gte=week_ago).count()
    
    # Top customers by order count
    top_customers = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).order_by('-order_count')[:5]
    
    # Top customers by spending (only from completed orders, not cancelled)
    top_spenders = User.objects.annotate(
        total_spent=Sum('orders__total_amount', filter=Q(orders__status__in=['Paid', 'Confirmed', 'Processing', 'Shipped', 'Delivered']))
    ).filter(total_spent__gt=0).order_by('-total_spent')[:5]
    
    context = {
        # Order stats
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'recent_orders': recent_orders,
        
        # Revenue stats
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        
        # Product stats
        'total_products': total_products,
        'active_products': active_products,
        'featured_products': featured_products,
        'low_stock_products': low_stock_products,
        
        # Category stats
        'total_categories': total_categories,
        'active_categories': active_categories,
        
        # Payment stats
        'cod_orders': cod_orders,
        'online_payments': online_payments,
        'pending_refunds': pending_refunds,
        
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'recent_users': recent_users,
        
        # Lists
        'recent_orders_list': recent_orders_list,
        'top_products': top_products,
        'top_customers': top_customers,
        'top_spenders': top_spenders,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_orders(request):
    """Admin orders management page"""
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(shipping_name__icontains=search)
        )
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'admin/orders.html', context)


@staff_member_required
def admin_products(request):
    """Admin products management page"""
    products = Product.objects.select_related('category').order_by('-created_at')
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)
    elif status_filter == 'featured':
        products = products.filter(is_featured=True)
    elif status_filter == 'low_stock':
        products = products.filter(stock__lt=10)
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'admin/products.html', context)


@staff_member_required
def admin_payments(request):
    """Admin payments management page"""
    payments = Payment.objects.select_related('order', 'order__user').order_by('-created_at')
    
    # Filter by payment method
    method_filter = request.GET.get('method')
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Filter by refund status
    refund_filter = request.GET.get('refund')
    if refund_filter:
        payments = payments.filter(refund_status=refund_filter)
    
    context = {
        'payments': payments,
        'method_filter': method_filter,
        'status_filter': status_filter,
        'refund_filter': refund_filter,
    }
    
    return render(request, 'admin/payments.html', context)


@staff_member_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('admin_orders')


@staff_member_required
def update_payment_status(request, payment_id):
    """Update payment status"""
    if request.method == 'POST':
        payment = Payment.objects.get(id=payment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Payment.PAYMENT_STATUS_CHOICES):
            payment.payment_status = new_status
            if new_status == 'Success' and not payment.payment_date:
                payment.payment_date = timezone.now()
            payment.save()
            messages.success(request, f'Payment status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('admin_payments')
