from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to="products/")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > self.discount_price:
            return round(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product.final_price * self.quantity

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Payment_Pending', 'Payment Pending'),
        ('Paid', 'Paid'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Payment_Pending')
    
    # Address details
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Cancellation fields
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    is_cancellable = models.BooleanField(default=True)

    def __str__(self):
        return f"Order {self.order_number}"

    @classmethod
    def generate_order_number(cls):
        import uuid
        return f"DD{str(uuid.uuid4())[:8].upper()}"
    
    def can_be_cancelled(self):
        """Check if order can be cancelled (within 24 hours and not shipped)"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Can't cancel if already cancelled or delivered
        if self.status in ['Cancelled', 'Delivered']:
            return False
        
        # Can't cancel if shipped
        if self.status == 'Shipped':
            return False
        
        # Can cancel within 24 hours of order creation
        if self.created_at + timedelta(hours=24) > timezone.now():
            return True
        
        return False
    
    def get_cancellation_deadline(self):
        """Get the deadline for order cancellation"""
        from datetime import timedelta
        return self.created_at + timedelta(hours=24)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI Payment'),
        ('CARD', 'Credit/Debit Card'),
        ('NETBANKING', 'Net Banking'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]
    
    REFUND_STATUS_CHOICES = [
        ('Not_Required', 'Not Required'),
        ('Pending', 'Refund Pending'),
        ('Processing', 'Refund Processing'),
        ('Completed', 'Refund Completed'),
        ('Failed', 'Refund Failed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Refund fields
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='Not_Required')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    refund_initiated_at = models.DateTimeField(blank=True, null=True)
    refund_completed_at = models.DateTimeField(blank=True, null=True)
    refund_expected_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment for {self.order.order_number}"
    
    def initiate_refund(self):
        """Initiate refund process"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.payment_status == 'Success' and self.refund_status == 'Not_Required':
            self.refund_status = 'Pending'
            self.refund_amount = self.amount
            self.refund_initiated_at = timezone.now()
            self.refund_expected_date = timezone.now() + timedelta(days=4)
            self.save()
            return True
        return False
    
    def get_refund_timeline(self):
        """Get refund timeline information"""
        if self.refund_status == 'Not_Required':
            return "No refund required"
        
        if self.refund_expected_date:
            return f"Expected refund date: {self.refund_expected_date.strftime('%B %d, %Y')}"
        
        return "Refund timeline not available"