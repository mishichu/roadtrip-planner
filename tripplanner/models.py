from django.db import models
from django.contrib.auth.models import User
from address.models import AddressField
from django_google_maps import fields as map_fields
import os

from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="profile")
    user_bio = models.CharField(max_length=1000, blank=True)
    following = models.ManyToManyField(User, related_name='following')
    user_picture = models.ImageField(upload_to='media', default='default.jpg')
    address = models.CharField(blank=True, null=True, max_length=300)
                                    
    def __str__(self):
        return 'Profile(id=' + str(self.id) + ')'
    
class EmailItem(models.Model):
    email_addr = models.EmailField()
    received_email = models.BooleanField(default=False)

    def __str__(self):
        return "EmailItem(id="+ str(self.id) + ")"

class TripItem(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_by")
    creation_time = models.DateTimeField() 

    title = models.CharField(max_length=100)
    published = models.BooleanField(default=False)
    
    starting_from = models.CharField(max_length= 300)

    start_date = models.DateTimeField()
    
    ending_at = models.CharField(max_length= 300)

    end_date = models.DateTimeField()

    invited_friends = models.ManyToManyField(User)
    email_invites = models.ManyToManyField(EmailItem)
    
    notes = models.CharField(max_length=1000, blank=True)
                                    
    def __str__(self):
        return 'Trip(id=' + str(self.id) + ')'

class LocationItem(models.Model):
    address = models.CharField(max_length= 300)
 
    trip = models.ForeignKey(TripItem, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    notes = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return 'Location(id=' + str(self.id) + ')'
