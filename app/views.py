from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages
from .models import Destination, Package, Booking
from .forms import BookingForm, DestinationForm, PackageForm
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.paginator import Paginator
import razorpay


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        # Check if the user is an admin (you can replace this with your own logic or use is_staff)
        if request.user.is_admin:  # Assuming you have an 'is_admin' attribute or method
            return redirect('adminhome')
        else:
            # Redirect non-admin users to a different page if needed
            return redirect('home')  # Modify 'home' as per your requirement

    else:
        # If the user is not authenticated, proceed with login attempt
        if request.method == 'POST':
            email = request.POST['email'].lower()  # Convert email to lowercase for case-insensitive comparison
            password = request.POST['password']
            # Authenticate the user with email and password
            user = authenticate(request, username=email, password=password)  # Pass 'request' here
            if user is not None:
                login(request, user)
                # After login, redirect based on whether the user is admin or not
                if user.is_admin:  # Assuming you have an 'is_admin' attribute or method
                    return redirect('adminhome')
                else:
                    return redirect('home')  # Non-admin users should go to a different page
            else:
                messages.error(request, "Email or Password is incorrect. Please check caps lock also!")
                return render(request, 'superuser/login.html')

        else:
            return render(request, 'superuser/login.html')


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    logout(request)
    return redirect('login')



# Admin home view
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminhome(request):
    if request.user.is_admin:
        # Calculate total earnings
        total_earnings = Booking.objects.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0

        # Calculate earnings in the previous time period (e.g., previous month or week)
        today = now().date()
        previous_start_date = today - timedelta(days=30)  # Adjust the period as needed
        previous_earnings = Booking.objects.filter(
            status='confirmed', created_at__date__gte=previous_start_date, created_at__date__lt=today
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Calculate earnings growth percentage
        earnings_growth_percentage = 0  # Default if no previous earnings
        if previous_earnings > 0:
            earnings_growth_percentage = ((total_earnings - previous_earnings) / previous_earnings) * 100

        # Count total bookings
        total_bookings = Booking.objects.filter(status='confirmed').count()

        # Calculate growth percentage for bookings
        previous_total_bookings = Booking.objects.filter(
            status='confirmed', created_at__date__gte=previous_start_date, created_at__date__lt=today
        ).count()
        bookings_growth_percentage = 0  # Default if no previous bookings
        if previous_total_bookings > 0:
            bookings_growth_percentage = ((total_bookings - previous_total_bookings) / previous_total_bookings) * 100

        # Fetch booking history (e.g., the last 10 bookings)
        booking_history = Booking.objects.order_by('-id')[:10]

        context = {
            'total_earnings': total_earnings,
            'earnings_growth_percentage': earnings_growth_percentage,  # Added earnings growth
            'total_bookings': total_bookings,
            'bookings_growth_percentage': bookings_growth_percentage,  # Added bookings growth
            'booking_history': booking_history,
        }
        return render(request, 'superuser/adminhome.html', context)
    else:
        return redirect('home')

        

# List all destinations for the admin
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def allpackcat(request):
    destinations = Destination.objects.all()
    
    # Prepare data including only the total tours for each destination
    destination_data = []
    for destination in destinations:
        total_tours = destination.packages.count()  # Count of packages related to each destination
        destination_data.append({
            'id': destination.id,
            'name': destination.name,
            'total_tours': total_tours,
        })

    # Set up pagination for the destination data
    paginator = Paginator(destination_data, 10)  # Show 10 destinations per page
    page_number = request.GET.get('page')  # Get the page number from the request
    destinations_page = paginator.get_page(page_number)  # Get the destinations for the current page

    return render(request, 'superuser/allpackagecategories.html', {
        'destinations': destinations_page
    })



# Add a new destination (package category)
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addpackcat(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = DestinationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('allpackcat')  # Redirect to all categories view
        else:
            form = DestinationForm()
        return render(request, 'superuser/addpackagecategory.html', {'form': form})
    
    else:
        return redirect('home')

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_package_category(request, id):
    if request.user.is_admin:
        destination = get_object_or_404(Destination, id=id)

        if request.method == 'POST':
            form = DestinationForm(request.POST, instance=destination)
            if form.is_valid():
                form.save()
                return redirect('allpackcat')  # Redirect to the main listing page after saving
        else:
            form = DestinationForm(instance=destination)

        return render(request, 'superuser/addpackagecategory.html', {
            'form': form,
            'is_edit': True  # Pass a flag to identify edit mode
        })

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_package_category(request, id):
    if request.user.is_admin:
        # Add logic to delete a package category
        destination = get_object_or_404(Destination, id=id)
        destination.delete()
        return redirect('allpackcat')  # Redirect to the main listing page after deletion


# Add a new package
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addnewpack(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = PackageForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('allpac')  # Redirect to all packages view
        else:
            form = PackageForm()

        destinations = Destination.objects.all()
        return render(request, 'superuser/addnewpackage.html', {'form': form, 'destinations': destinations})

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def package_edit(request, pk):
    if request.user.is_admin:
        package = get_object_or_404(Package, pk=pk)

        if request.method == 'POST':
            form = PackageForm(request.POST, instance=package)
            if form.is_valid():
                form.save()
                return redirect('allpac')  # Redirect to the package list after updating
        else:
            form = PackageForm(instance=package)

        destinations = Destination.objects.all()
        return render(request, 'superuser/addnewpackage.html', {
            'form': form,
            'is_edit': True,  # Indicate that this is edit mode
            'package': package,
            'destinations': destinations
        })

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def package_delete(request, pk):
    if request.user.is_admin:
        package = get_object_or_404(Package, pk=pk)
        package.delete()
        return redirect('allpac')  # Redirect to the list of packages after deletion


# List all packages
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def allpac(request):
    packages = Package.objects.all()
    paginator = Paginator(packages, 10)  # Show 10 packages per page
    page_number = request.GET.get('page')  # Get the page number from the request
    packages = paginator.get_page(page_number)  # Get the packages for the current page

    return render(request, 'superuser/allpackages.html', {'packages': packages})


def booking_create(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.package = package
            booking.total_amount = booking.calculate_total_amount()
            booking.save()
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, 'booking_form.html', {'form': form, 'package': package})


def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})


def booking_confirm(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment_failed.html', {"error": "Payment verification failed"})

        # Update booking status to confirmed
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.status = 'confirmed'
            booking.save()
            return render(request, 'payment_success.html', {'booking': booking})
        except Booking.DoesNotExist:
            return render(request, 'payment_failed.html', {"error": "Booking does not exist"})

    return JsonResponse({'error': 'Invalid request'}, status=400)

