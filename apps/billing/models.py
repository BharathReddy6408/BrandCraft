from django.db import models
from django.conf import settings
from subscriptions.models import UserSubscription

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('PAID', 'Paid'),
        ('VOID', 'Void'),
        ('UNCOLLECTIBLE', 'Uncollectible'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    invoice_number = models.CharField(max_length=50, unique=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    provider_invoice_id = models.CharField(max_length=255, blank=True, null=True)
    invoice_pdf_url = models.URLField(max_length=500, blank=True, null=True)
    
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username} ({self.status})"

class PaymentMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    provider_payment_method_id = models.CharField(max_length=255)
    
    # e.g., 'card', 'upi', 'netbanking'
    method_type = models.CharField(max_length=50, default='card') 
    
    # Optional mask fields for display (e.g., **** **** **** 4242)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True) # Visa, Mastercard, RuPay
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} ending in {self.last4} ({self.user.username})"
