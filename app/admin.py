from django.contrib import admin
from .models import Package, Booking, Destination
from django.contrib.auth.admin import UserAdmin
from . models import Account

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username','date_joined', 'last_login', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
# admin.site.register(CustomUser)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'adult_price', 'child_price')
    search_fields = ('name', 'destination__name')
    ordering = ('name',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'package', 'arrival_date', 'departure_date', 'num_adults', 'num_children', 'total_amount')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('package', 'arrival_date', 'departure_date')
    ordering = ('arrival_date',)

# Register your models here
admin.site.register(Package, PackageAdmin)
admin.site.register(Booking, BookingAdmin)