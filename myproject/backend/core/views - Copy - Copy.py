from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import User, Produce, Order, FarmerProfile, RestaurantProfile
from .forms import FarmerRegistrationForm, RestaurantRegistrationForm, ProduceForm, OrderForm


def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def register_farmer(request):
    """Farmer registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please login instead.')
                return render(request, 'register.html', {'form': form, 'role': 'farmer', 'email_exists': True})
            
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to AgriConnect, {user.first_name}! Your farmer account has been created.')
            return redirect('farmer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FarmerRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'farmer'})


def register_restaurant(request):
    """Restaurant registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RestaurantRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please login instead.')
                return render(request, 'register.html', {'form': form, 'role': 'restaurant', 'email_exists': True})
            
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to AgriConnect! Your restaurant account has been created.')
            return redirect('restaurant_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RestaurantRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'role': 'restaurant'})


def user_login(request):
    """Login view for both farmers and restaurants"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'farmer')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.role == role:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, f'This account is registered as a {user.get_role_display()}, not a {role}.')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'login.html')


def user_logout(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.is_farmer():
        return redirect('farmer_dashboard')
    elif request.user.is_restaurant():
        return redirect('restaurant_dashboard')
    return redirect('home')


@login_required
def farmer_dashboard(request):
    """Farmer dashboard view"""
    if not request.user.is_farmer():
        messages.error(request, 'Access denied. This page is for farmers only.')
        return redirect('dashboard')
    
    # Get farmer's produce listings
    produce_listings = Produce.objects.filter(farmer=request.user)
    
    # Get incoming orders/requests
    incoming_orders = Order.objects.filter(farmer=request.user).select_related('restaurant', 'produce')
    
    # Stats
    total_produce = produce_listings.count()
    available_produce = produce_listings.filter(status='available').count()
    pending_orders = incoming_orders.filter(status='pending').count()
    
    context = {
        'produce_listings': produce_listings,
        'incoming_orders': incoming_orders,
        'total_produce': total_produce,
        'available_produce': available_produce,
        'pending_orders': pending_orders,
        'form': ProduceForm(),
    }
    return render(request, 'farmer_dashboard.html', context)


@login_required
def add_produce(request):
    """Add new produce listing"""
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProduceForm(request.POST)
        if form.is_valid():
            produce = form.save(commit=False)
            produce.farmer = request.user
            produce.save()
            messages.success(request, f'Successfully added {produce.name} to your listings!')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    
    return redirect('farmer_dashboard')


@login_required
def update_order_status(request, order_id, status):
    """Accept or reject an order"""
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    order = get_object_or_404(Order, id=order_id, farmer=request.user)
    
    if status in ['accepted', 'rejected']:
        order.status = status
        order.save()
        
        if status == 'accepted':
            # Update produce quantity
            produce = order.produce
            produce.quantity -= order.quantity_requested
            produce.update_status()
            messages.success(request, f'Order #{order.id} has been accepted!')
        else:
            messages.info(request, f'Order #{order.id} has been rejected.')
    
    return redirect('farmer_dashboard')


@login_required
def restaurant_dashboard(request):
    """Restaurant dashboard view"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied. This page is for restaurants only.')
        return redirect('dashboard')
    
    # Get all available produce from farmers
    available_produce = Produce.objects.filter(
        status__in=['available', 'pending']
    ).select_related('farmer')
    
    # Get restaurant's orders
    my_orders = Order.objects.filter(restaurant=request.user).select_related('farmer', 'produce')
    
    # Stats
    total_farmers = User.objects.filter(role='farmer').count()
    total_produce = available_produce.count()
    pending_orders = my_orders.filter(status='pending').count()
    
    context = {
        'available_produce': available_produce,
        'my_orders': my_orders,
        'total_farmers': total_farmers,
        'total_produce': total_produce,
        'pending_orders': pending_orders,
    }
    return render(request, 'restaurant_dashboard.html', context)


@login_required
def request_supply(request, produce_id):
    """Request supply from a farmer"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    produce = get_object_or_404(Produce, id=produce_id)
    
    if request.method == 'POST':
        quantity = request.POST.get('quantity', '').strip()
        
        # Handle empty quantity
        if not quantity:
            messages.error(request, 'Please enter a quantity.')
            return redirect('restaurant_dashboard')
        
        try:
            # Replace comma with period for decimal parsing
            quantity = quantity.replace(',', '.')
            quantity = float(quantity)
            
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than zero.')
                return redirect('restaurant_dashboard')
            
            if quantity > float(produce.quantity):
                messages.error(request, f'Requested quantity exceeds available stock ({produce.quantity} kg).')
                return redirect('restaurant_dashboard')
            
            # Create order
            from decimal import Decimal
            order = Order.objects.create(
                restaurant=request.user,
                farmer=produce.farmer,
                produce=produce,
                quantity_requested=Decimal(str(quantity))
            )
            messages.success(request, f'✅ Supply request sent to {produce.farmer.first_name} for {quantity} kg of {produce.name}!')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Please enter a valid number for quantity.')
    
    return redirect('restaurant_dashboard')


def check_email(request):
    """AJAX endpoint to check if email already exists"""
    email = request.GET.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})


# Import JsonResponse for AJAX
from django.http import JsonResponse
