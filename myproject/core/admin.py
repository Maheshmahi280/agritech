from django.contrib import admin
from .models import User, FarmerProfile, RestaurantProfile, Produce, Order


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'farm_name', 'location']
    search_fields = ['user__username', 'farm_name', 'location']


@admin.register(RestaurantProfile)
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant_name', 'restaurant_type']
    list_filter = ['restaurant_type']
    search_fields = ['restaurant_name']


@admin.register(Produce)
class ProduceAdmin(admin.ModelAdmin):
    list_display = ['name', 'farmer', 'quantity', 'price_per_kg', 'status', 'availability_date']
    list_filter = ['status', 'availability_date']
    search_fields = ['name', 'farmer__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'restaurant', 'farmer', 'produce', 'quantity_requested', 'total_price', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['restaurant__username', 'farmer__username', 'produce__name']
