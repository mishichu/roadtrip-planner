from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
import datetime
import json
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from tripplanner.forms import *
from tripplanner.models import *

# for string similarity
import difflib

@login_required
@login_required
def profile(request, id):
    #find_user = User.objects.get(id = id)
    curr_user = Profile.objects.get(user = request.user)
    all_trips = list(TripItem.objects.all().order_by('creation_time'))
    
    try:
        find_user = User.objects.get(id = id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'error': "Profile does not exist."})

    if id == curr_user.id:
        if request.method == 'POST':
            if 'bio_input_text' in request.POST:
                curr_user.user_bio = request.POST['bio_input_text']
                curr_user.save()
            if 'profile_picture' in request.FILES:
                curr_user.user_picture = request.FILES['profile_picture']
                curr_user.save()

        following = list(map(lambda user: Profile.objects.get(user=user), curr_user.following.all()))
        followed_by = list(filter(lambda profile: request.user in profile.following.all(), Profile.objects.all()))                

        trips = []
        invited_to_trips = []
        for trip in all_trips:
            if trip.created_by.id == request.user.id:
                trips.append(trip)
            elif request.user in trip.invited_friends.all():
                invited_to_trips.append(trip)
            else:
                for email in trip.email_invites.all():
                    if email.email_addr == request.user.email:
                        invited_to_trips.append(trip)
                        break
            
                    
        context = {'viewing': curr_user,
                   'following':following,
                   'followed_by':followed_by,
                   'user_trips':trips,
                   'friend_trips': invited_to_trips}
        
    else:
        curr_profile = Profile.objects.get(user = find_user)
        context = {'viewing': curr_profile}
        if 'follow' in request.GET:
            curr_user.following.add(curr_profile.user)
            curr_user.save()

        if 'unfollow' in request.GET:
            curr_user.following.remove(curr_profile.user)
            curr_user.save()

        context['is_following'] = (curr_profile.user in curr_user.following.all())

        following = list(map(lambda user: Profile.objects.get(user=user), curr_profile.following.all()))
        followed_by = list(filter(lambda profile: find_user in profile.following.all(), Profile.objects.all()))

        trips = []
        #gets all trips authored or viewable by the user whose profile is being viewed only if
        #the user is friends with the logged in user
        if find_user in curr_user.following.all():
            for trip in all_trips:
                if trip.created_by.id == find_user.id:
                    trips.append(trip)
                #if trip.created_by.id == find_user.id and request.user.email in trip.email_invites.all():
                    #trips.append(trip)
                #elif find_user.email in trip.email_invites.all():
                    #trips.append(trip)
                #elif find_user in trip.invited_friends.all():
                    #trips.append(trip)
        context['user_trips'] = trips
        context['following'] = following
        context['followed_by']= followed_by
        
                
    return render(request, 'profile.html', context)

@login_required
def home_action(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'home.html', context)
@login_required

def friends_action(request):
    context = {}
    curr_user = Profile.objects.get(user = request.user)
    search_text = None
    results = []

    if request.method == 'GET':
        for x in request.GET:
            if 'unfollow' in x:
                curr_user.following.remove(User.objects.get(id=x[len('unfollow_'):len(x)]))
                curr_user.save()
            elif 'follow' in x:
                curr_user.following.add(User.objects.get(id=x[len('follow_'):len(x)]))
                curr_user.save()
        
        if 'search_text' in request.GET:
            search_text = request.GET['search_text']

    else:
        search_text = request.POST['search_text']

    context['following'] = curr_user.following.all()

    if search_text:
        res = []
        for user in User.objects.all():
            matches = list(map(lambda x: x.lower(), [user.first_name, user.last_name, user.first_name + " " +user.last_name, user.email, user.username]))
            if len(difflib.get_close_matches(search_text.lower(), matches)) > 0:
                res.append(Profile.objects.get(user = user))
        context['search_text'] = search_text          
        context['results'] = res
        
    return render(request, 'friends.html', context)

@login_required
def create_trip_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = CreateTripItem()
        return render(request, 'map.html', context)

    form = CreateTripItem(request.POST)
    if not form.is_valid():
        context = {'form': form}
        return render(request, 'map.html', context)
    
    new_trip = TripItem()
    new_trip.title = request.POST['title']
    new_trip.start_date = request.POST['start_date']
    new_trip.end_date = request.POST['end_date']
    new_trip.created_by = request.user
    new_trip.creation_time = timezone.now()
    new_trip.starting_from = request.POST['starting_from']
    new_trip.ending_at = request.POST['ending_at']
    new_trip.save()
    context['trip'] = new_trip
    context['form'] = form
    context['waypoints'] = []
    if new_trip.start_date > new_trip.end_date: 
        context['warning'] = '(Warning: start date should be before end date.)'

    return render(request, 'map_edit.html', context) 

def edit_trip_action(request, id):
    
    if request.method == 'GET':
        try:
            entry = TripItem.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'error': "Trip with id={id} does not exist."})
        if request.user != entry.created_by:
            return render(request, 'error.html', {'error': "You cannot edit other's trips."})
        form = CreateTripItem(instance=entry)
        waypoints = [l for l in LocationItem.objects.filter(trip=entry).order_by('start_date').values()]
        for loc in waypoints:
            loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
            loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
        context = {'form': form, 'trip': entry, 'waypoints': waypoints}
        print(waypoints)
        if entry.start_date > entry.end_date: 
            context['warning'] = '(Warning: start date should be before end date.)'
        return render(request, 'map_edit.html', context)
    try:
        entry = TripItem.objects.get(id=id)
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'error': "Trip with id={id} does not exist."})
    if request.user != entry.created_by:
        return render(request, 'error.html', {'error': "You cannot edit other's trips."})
    waypoints = [l for l in LocationItem.objects.filter(trip=entry).order_by('start_date').values()]
    for loc in waypoints:
        loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
        loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
    form = CreateTripItem(request.POST, instance=entry)
    if not form.is_valid():
        print("the form is not valid")
        context = {'form': form, 'trip': entry, 'waypoints': waypoints}
        return render(request, 'map_edit.html', context)
    entry.save()

    form = CreateTripItem(instance=entry)
    context = {
        'message': "Changes Saved.",
        'trip': entry,
        'form': form,
        'waypoints': waypoints,
    }
    if entry.start_date > entry.end_date: 
        context['warning'] = '(Warning: start date should be before end date.)'
    return render(request, 'map_edit.html', context)
    
def next_add_stops_action(request, id):
    if request.method == 'POST':
        form = CreateLocationItem()
        trip = TripItem.objects.get(id=id)
        waypoints = [l for l in LocationItem.objects.filter(trip=trip).order_by('start_date').values()]
        for loc in waypoints:
            loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
            loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
        context = {'form': form, 'trip': trip, 'waypoints': waypoints}
        return render(request, 'map2.html', context)


def next_invite_friends_action(request, id):
    context = {}
    find_user = User.objects.get(id = request.user.id)
    curr_user = Profile.objects.get(user = request.user)
    friends = []
    for person in curr_user.following.all():
        person_profile = Profile.objects.get(user = person)
        if request.user in person_profile.following.all():
            friends.append(person_profile)
    trip = TripItem.objects.get(id=id)
    context['curr_user'] = curr_user
    context['friends'] = friends
    context['trip_id'] = id
    context['trip'] = trip
    waypoints = [l for l in LocationItem.objects.filter(trip=trip).order_by('start_date').values()]
    for loc in waypoints:
        loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
        loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
    context['waypoints'] = waypoints
    if request.method == 'POST':
        print("Posty")
    return render(request, 'map3.html', context)

def addfriend(request, id):
    trip = TripItem.objects.get(id = id)
    if 'emailSelect' in request.POST and request.POST['emailSelect']:
        email_addr = request.POST['emailSelect']
        to_add = True
        for email in trip.email_invites.all():
            if email.email_addr == email_addr:
                to_add = False
                break
        if to_add: 
            email_item = EmailItem(email_addr=email_addr)
            email_item.save()
            trip.email_invites.add(email_item)
            trip.save()  
    return next_invite_friends_action(request, id)
    if 'drop1' in request.POST and request.POST['drop1']: 
        friend_id = request.POST['drop1']
        friend = User.objects.get(id = friend_id)
        if friend not in trip.invited_friends.all():
            trip.invited_friends.add(friend)
            trip.save()
    return next_invite_friends_action(request, id)

def next_review_trip_action(request, id):
    if request.method == 'POST':
        
        try:
            trip = TripItem.objects.get(id = id)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'error': "Trip with id={id} does not exist."})
        if request.user != trip.created_by:
            return render(request, 'error.html', {'error': "You cannot edit other's trips."})
        form = ReviewTripItem(instance = trip)
        context = {'form': form, 'trip': trip}
        waypoints = [l for l in LocationItem.objects.filter(trip=trip).order_by('start_date').values()]
        for loc in waypoints:
            loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
            loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
        context['waypoints'] = waypoints
        context['start_date'] = trip.start_date.date()
        context['end_date'] = trip.end_date.date()

        if context['start_date'] > context['end_date']:
            context['warning'] = '(Warning: start date should be before end date.)'
        return render(request, 'mapreview.html', context)
    return render(request, 'error.html', {'error': "Must be POST request."})

def publish_trip_action(request, id):
    if request.method == 'POST':
        try:
            trip = TripItem.objects.get(id=id)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'error': "Trip with id={id} does not exist."})
        if request.user != trip.created_by:
            return render(request, 'error.html', {'error': "You cannot edit other's trips."})
        trip.notes = request.POST['notes']
        trip.published = True
        trip.save()
        for email in trip.email_invites.all():
            context = {}
            context['sender'] = request.user.first_name + " " + request.user.last_name
            context['trip_title'] = trip.title
            context['email'] = email
            context['trip_id'] = trip.id
            if email.received_email == False:
                html_message = html_message = render_to_string('invitation_email.html', context)
                res = send_mail("road trip!", "hi", "roadtripwebapps@gmail.com", [email.email_addr], html_message=html_message)
                email.received_email = True
                email.save()
        return redirect('profile', id= request.user.id)
    return render(request, 'error.html', {'error': "Must be POST request."})  


def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    print(message)
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_stop_action(request, loc_id):
    try:
        new_item = LocationItem.objects.get(id=loc_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Stop with id={loc_id} does not exist.", status=404)
    response_data = {
        'address': new_item.address,
        'id': new_item.id,
        'start_date': new_item.start_date.strftime('%Y-%m-%dT%H:%M'),
        'end_date': new_item.end_date.strftime('%Y-%m-%dT%H:%M'),
        'notes': new_item.notes,
    }
    response_json = json.dumps(response_data)
    msg = "The operation has been received correctly."  
    print(response_json)
    return HttpResponse(response_json, content_type='application/json')
def view_trip_action(request, id):
    if request.method == 'GET':
        try:
            trip = TripItem.objects.get(id = id)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'error': "Trip with id={id} does not exist."})
        curr_user = Profile.objects.get(user = request.user)
        following = curr_user.following.all()
        invited_friends = trip.invited_friends.all()
        email_invites = trip.email_invites.all()

        b = (trip.created_by in following)
        b = b or (request.user == trip.created_by)
        b = b or (request.user in invited_friends)
        b = b or (len(filter(lambda x: x.email_addr == request.user.email, email_invites))>0)
        b = b or (len(filter(lambda x: x in following, invited_friends))>0)
        
        following_email = False
        for invite in email_invites:
            find_user = User.objects.get(email = invite.email_addr) 
            if find_user and find_user in following:
                following_email = True
                break
        b = b or following_email

        if not b: 
            return render(request, 'error.html', {'error': "You do not have access to view this trip."})
        context = {"trip": trip}
        waypoints = [l for l in LocationItem.objects.filter(trip=trip).order_by('start_date').values()]
        for loc in waypoints:
            loc['start_date'] = loc['start_date'].strftime('%m/%d/%Y, %H:%M')
            loc['end_date'] = loc['end_date'].strftime('%m/%d/%Y, %H:%M')
        context['waypoints'] = waypoints
        context['start_date'] = trip.start_date.date()
        context['end_date'] = trip.end_date.date()
        return render(request, 'viewmode_map.html', context)
        
    return render(request, 'error.html', {'error': "Must be GET request."})  

def add_stops_action(request):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)
    
    trip = TripItem.objects.get(id=request.POST['trip_id'])

    if request.user != trip.created_by:
        return _my_json_error_response("You cannot add stops to another's trip", status=403)
    
    #validation

    new_item = LocationItem(address = request.POST['address'],
                            start_date = request.POST['start_date'],
                            end_date = request.POST['end_date'],
                            notes = request.POST['notes'],
                            trip = trip)
    form = CreateLocationItem(request.POST, instance=new_item)
    if not form.is_valid():
        print("5")
        return _my_json_error_response("Error in one or more fields.", status=403)
    new_item.save()
    response_data = {
        'address': new_item.address,
        'id': new_item.id,
        'start_date': new_item.start_date.strftime('%m/%d/%Y, %H:%M'),
        'end_date': new_item.end_date.strftime('%m/%d/%Y, %H:%M'),
        'notes': new_item.notes,
        'type': "add",
    }
    print(response_data)
    response_json = json.dumps(response_data)
    msg = "The operation has been received correctly."  
    return HttpResponse(response_json, content_type='application/json')

def edit_stop_action(request, loc_id):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    if not request.user.id:
        print("1")
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    trip = TripItem.objects.get(id=request.POST['trip_id'])

    if request.user != trip.created_by:
        print("2")
        return _my_json_error_response("You cannot edit stops from another's trip", status=403)
    
    try:
        new_item = LocationItem.objects.get(id=loc_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Item with id={loc_id} does not exist.", status=404)
    
    new_item = LocationItem.objects.get(id=loc_id)
    form = CreateLocationItem(request.POST, instance=new_item)
    if not form.is_valid():
        print("5")
        return _my_json_error_response("Error in one or more fields.", status=403)
    
    new_item.save()
    response_data = {
        'address': new_item.address,
        'id': new_item.id,
        'start_date': new_item.start_date.strftime('%m/%d/%Y, %H:%M'),
        'end_date': new_item.end_date.strftime('%m/%d/%Y, %H:%M'),
        'notes': new_item.notes,
        'type': "edit",
    }
    print(response_data)
    response_json = json.dumps(response_data)
    msg = "The operation has been received correctly."  
    return HttpResponse(response_json, content_type='application/json')
    
    
def delete_stop_action(request, loc_id):
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)
    try:
        new_item = LocationItem.objects.get(id=loc_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Item with id={loc_id} does not exist.", status=404)
    
    trip = new_item.trip
    if request.user != trip.created_by:
        return _my_json_error_response("You cannot delete stops to another's trip",status=403)
    response_data = {
        'address': new_item.address,
        'id': new_item.id,
        'start_date': new_item.start_date.strftime('%m/%d/%Y, %H:%M'),
        'end_date': new_item.end_date.strftime('%m/%d/%Y, %H:%M'),
        'notes': new_item.notes,
    }
    response_json = json.dumps(response_data)

    
    new_item.delete()
    msg = "The operation has been received correctly."  
    return HttpResponse(response_json, content_type='application/json')

def login_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'login.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse(''))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context = { 'form': RegisterForm() }
        return render(request, 'register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['email'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['email'],
                            password=form.cleaned_data['password'])

    new_profile = Profile(user = new_user)
    new_profile.save()

    login(request, new_user)
    return redirect(reverse(''))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))
