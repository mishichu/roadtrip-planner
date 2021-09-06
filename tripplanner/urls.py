  
from django.urls import path
from tripplanner import views

urlpatterns = [
    path('', views.home_action, name=''),
    path('create', views.create_trip_action, name='create'),
    path('edit/<int:id>', views.edit_trip_action, name="edit"),
    path('login', views.login_action, name='login'),
    path('register', views.register_action, name='register'),
    path('logout', views.logout_action, name='logout'),
    path('friends', views.friends_action, name='friends'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('next-add-stops/<int:id>', views.next_add_stops_action, name="next-add-stops"),
    path('next-invite-friends/<int:id>', views.next_invite_friends_action, name="next-invite-friends"),
    path('next-review-trip/<int:id>', views.next_review_trip_action, name="next-review-trip"),
    path('publish-trip/<int:id>',views.publish_trip_action, name="publish-trip"),
    path('view-trip/<int:id>', views.view_trip_action, name="view-trip"),
    path('add-stops', views.add_stops_action, name="add-stops"),
    path('delete-stop/<int:loc_id>', views.delete_stop_action, name="delete-stop"),
    path('edit-stop/<int:loc_id>', views.edit_stop_action, name="edit-stop"),
    path('get-stop/<int:loc_id>', views.get_stop_action, name="get-stop"),
    path('addfriend/<int:id>', views.addfriend, name="addfriend"),

]
