def cart_context(request):
    """Add cart information to all templates"""
    from .models import Category
    
    context = {}
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            context['cart_items_count'] = cart.total_items
        except:
            context['cart_items_count'] = 0
    else:
        context['cart_items_count'] = 0
    
    # Add categories for footer
    context['footer_categories'] = Category.objects.filter(is_active=True)[:4]
    return context
