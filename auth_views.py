from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'auth/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    
    return render(request, 'auth/register.html')

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

@login_required
def profile_view(request):
    """User profile view"""
    from django.db.models import Sum
    from products.models import Order, Cart
    
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

# Custom Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        # Get the email from the form
        email = form.cleaned_data['email']
        
        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = self.request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            # Always send HTML email (both development and production)
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            
            # Render HTML email
            html_content = render_to_string('auth/password_reset_email.html', {
                'reset_link': reset_link,
                'user': user,
            })
            
            # Create email
            subject = 'Password Reset - D&D Salon'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [email]
            
            # Send HTML email only (no plain text)
            msg = EmailMultiAlternatives(subject, html_content, from_email, to_email)
            msg.content_subtype = "html"
            msg.send()
            
            if settings.DEBUG:
                logger.info(f"Password reset link for {email}: {reset_link}")
                messages.success(self.request, f'Password reset link sent to {email}. In development mode, check the console for the link.')
            else:
                messages.success(self.request, f'Password reset link sent to {email}.')
            
        except User.DoesNotExist:
            messages.error(self.request, 'No account found with this email address.')
            return self.form_invalid(form)
        
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'
