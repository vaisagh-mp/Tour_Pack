from django import forms
from .models import Booking, Destination, Package


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name']


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = '__all__'


class BookingForm(forms.ModelForm):
    arrival_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}))
    departure_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['name', 'phone', 'email', 'city', 'package', 'arrival_date',
                  'departure_date', 'num_adults', 'num_children', 'child_ages']
