from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based authentication"""
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('restaurant', 'Restaurant'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_farmer(self):
        return self.role == 'farmer'
    
    def is_restaurant(self):
        return self.role == 'restaurant'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class FarmerProfile(models.Model):
    """Extended profile for Farmers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.farm_name or self.user.username}'s Farm"


class RestaurantProfile(models.Model):
    """Extended profile for Restaurants"""
    RESTAURANT_TYPES = [
        ('fine-dining', 'Fine Dining'),
        ('casual', 'Casual Dining'),
        ('cafe', 'Cafe'),
        ('fast-food', 'Fast Food'),
        ('catering', 'Catering Service'),
        ('hotel', 'Hotel Restaurant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant_profile')
    restaurant_name = models.CharField(max_length=200)
    restaurant_type = models.CharField(max_length=50, choices=RESTAURANT_TYPES)
    address = models.TextField()
    gst_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.restaurant_name


class Produce(models.Model):
    """Produce listed by farmers"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold Out'),
    ]
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produce_listings')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    availability_date = models.DateField()
    contact_number = models.CharField(max_length=15, blank=True)  # Contact number for this produce
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Produce"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.farmer.username}"
    
    def update_status(self):
        """Auto-update status based on quantity"""
        if self.quantity <= 0:
            self.status = 'sold'
        elif self.quantity < 50:
            self.status = 'pending'  # Low stock
        else:
            self.status = 'available'
        self.save()


class Order(models.Model):
    """Orders/Requests from restaurants to farmers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    restaurant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_orders')
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE, related_name='orders')
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.produce.name}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity_requested * self.produce.price_per_kg
        super().save(*args, **kwargs)
