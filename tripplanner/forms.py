from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from tripplanner.models import Profile, TripItem, LocationItem
#from location_field.models.plain import PlainLocationField

#from geoposition.fields import GeopositionField


class DateInput(forms.DateInput):
    input_type = 'date'
    
class CreateProfile(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ()

class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user','following',)
        fields = {
            'user_bio': forms.Textarea(),
            'user_picture': forms.ImageField(),
        }
        enctype = "multipart/form-data"

class CreateLocationItem(forms.ModelForm):
    #trip_id = forms.IntegerField(attrs={'type': 'hidden'})
    class Meta:
        model = LocationItem
        exclude = ('trip',)
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 8}),
        }
        labels = {
            'address': "I want to visit...",
            'start_date': "Arrival Time",
            'end_date': "Departure Time",
            'notes': "Itinerary or any other travel notes:",
        }
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        print(start_date)
        print(end_date)
        if start_date and end_date and start_date > end_date:
            print("eeeeek")
            raise forms.ValidationError("Stop start date later than end date. Please change either the start or end date. ")
        return cleaned_data
        
class CreateTripItem(forms.ModelForm):
    class Meta:
        model = TripItem
        exclude = (
             'created_by',
            'creation_time',
            'published',
            'invited_friends',
            'notes',
            'trip_id',
            'email_invites',
        )
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
        labels = {
            'title': 'Trip Title',
            'starting_from': 'Starting From...',
            'ending_at': 'Ending At...',
        }
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        print(start_date)
        print(end_date)
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Trip start date later than end date. Please change either the start or end date. ")
        return cleaned_data


class ReviewTripItem(forms.ModelForm):
    class Meta:
        model = TripItem
        exclude = (
            'created_by',
            'creation_time',
            'published',
            'invited_friends',
            'trip_id',
            'email_invites',
            'title',
            'starting_from',
            'ending_at',
            'start_date',
            'end_date',
        )
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 8}),
        }
        labels = {
            'notes': "Add any other notes here:",
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 50)
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    password  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    confirm_password  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())

    #city = forms.CharField(max_length=255,required=False,label="(Optional) I'm starting my road trip from...")

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        print(password)
        print(confirm_password)
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("passwords did not match :(")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_email(self):
        # Confirms that the username is not already present in the
        # User model database.
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("Email is already registered.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return email
