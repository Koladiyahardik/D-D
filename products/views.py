from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import uuid

from .models import Category, Product, Cart, CartItem, Order, OrderItem, Payment


def home(request):
    """Home page with featured products and categories"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def products_list(request):
    """Products listing page with search and filter"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        products = products.filter(name__icontains=search)
    
    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'sort_by': sort_by,
    }
    return render(request, 'products/list.html', context)


def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product_id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)


def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')


def user_register(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    
    return render(request, 'auth/register.html')


def user_logout(request):
    """User logout"""
    logout(request)
    return redirect('home')


@login_required
def cart_view(request):
    """Cart page"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('products_list')


@login_required
def update_cart(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
        except CartItem.DoesNotExist:
            pass
    
    return redirect('cart_view')


@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart_view')


@login_required
def checkout(request):
    """Checkout page"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart_view')
    
    if request.method == 'POST':
        # Create order with payment pending status
        order = Order.objects.create(
            user=request.user,
            order_number=Order.generate_order_number(),
            shipping_name=request.POST.get('shipping_name'),
            shipping_phone=request.POST.get('shipping_phone'),
            shipping_address=request.POST.get('shipping_address'),
            shipping_city=request.POST.get('shipping_city'),
            shipping_state=request.POST.get('shipping_state'),
            shipping_pincode=request.POST.get('shipping_pincode'),
            total_amount=cart.total_amount,
            status='Payment_Pending'
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.final_price
            )
        
        # Store order ID in session for payment (no need to store cart items)
        request.session['order_id'] = order.id
        
        # Redirect to payment page
        return redirect('payment_selection', order_id=order.id)
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart/checkout.html', context)


@login_required
def orders_list(request):
    """User orders list"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/list.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail page"""
    # Allow admins to view any order, regular users can only view their own orders
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/detail.html', context)


@login_required
def user_profile(request):
    """User profile page"""
    from django.db.models import Sum
    
    # Calculate total amount spent (only from completed orders, not cancelled)
    total_spent = Order.objects.filter(
        user=request.user,
        status__in=['Paid', 'Confirmed', 'Processing', 'Shipped', 'Delivered']
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Get cart items count safely
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items_count = cart.total_items
    except Cart.DoesNotExist:
        cart_items_count = 0
    
    context = {
        'user': request.user,
        'total_spent': total_spent,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'auth/profile.html', context)


@login_required
def payment_selection(request, order_id):
    """Payment method selection page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'Payment_Pending':
        messages.error(request, 'This order is not eligible for payment')
        return redirect('orders_list')
    
    context = {
        'order': order,
    }
    return render(request, 'payment/selection.html', context)


@login_required
def process_payment(request, order_id):
    """Process payment based on selected method"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'Payment_Pending':
        messages.error(request, 'This order is not eligible for payment')
        return redirect('orders_list')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'COD':
            # Create payment record for COD
            payment = Payment.objects.create(
                order=order,
                payment_method='COD',
                payment_status='Success',
                amount=order.total_amount,
                payment_date=timezone.now()
            )
            
            # Update order status to Confirmed (not Paid, since payment is on delivery)
            order.status = 'Confirmed'
            order.save()
            
            # Clear cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.all().delete()
            
            messages.success(request, f'Order confirmed! You will pay ₹{order.total_amount} on delivery.')
            return redirect('payment_success', order_id=order.id)
        
        elif payment_method in ['UPI', 'CARD', 'NETBANKING']:
            # For online payments, create pending payment record
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                payment_status='Pending',
                amount=order.total_amount
            )
            
            # In a real application, you would integrate with payment gateway here
            # For demo purposes, we'll simulate successful payment
            payment.payment_status = 'Success'
            payment.transaction_id = f"TXN{str(uuid.uuid4())[:8].upper()}"
            payment.payment_date = timezone.now()
            payment.save()
            
            # Update order status
            order.status = 'Paid'
            order.save()
            
            # Clear cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.all().delete()
            
            messages.success(request, f'Payment successful! Transaction ID: {payment.transaction_id}')
            return redirect('payment_success', order_id=order.id)
    
    return redirect('payment_selection', order_id=order.id)


@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'payment/success.html', context)


@login_required
def payment_failed(request, order_id):
    """Payment failed page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'payment/failed.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel order page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_be_cancelled():
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        # Update order status
        order.status = 'Cancelled'
        order.cancelled_at = timezone.now()
        order.cancellation_reason = cancellation_reason
        order.is_cancellable = False
        order.save()
        
        # Initiate refund only if payment was made online (not COD)
        if hasattr(order, 'payment') and order.payment.payment_status == 'Success' and order.payment.payment_method != 'COD':
            order.payment.initiate_refund()
        
        messages.success(request, f'Order {order.order_number} has been cancelled successfully.')
        return redirect('cancellation_confirmation', order_id=order.id)
    
    context = {
        'order': order,
        'cancellation_deadline': order.get_cancellation_deadline(),
    }
    return render(request, 'orders/cancel.html', context)


@login_required
def cancellation_confirmation(request, order_id):
    """Cancellation confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status != 'Cancelled':
        messages.error(request, 'This order is not cancelled.')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/cancellation_confirmation.html', context)


@login_required
def refund_status(request, order_id):
    """Refund status page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not hasattr(order, 'payment') or order.payment.refund_status == 'Not_Required':
        messages.error(request, 'No refund information available for this order.')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/refund_status.html', context)