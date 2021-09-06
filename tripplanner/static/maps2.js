// Create the script tag, set the appropriate attributes
var script = document.createElement('script');
script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCtalreLvZ_sS089Vy_UtXyjXOX_sjbxHQ&callback=initialize&libraries=&libraries=geometry,places&v=weekly"
script.async = true;


var map, infoWindow, infoWindow2, directionsService, directionsRenderer;
var startLoc, endLoc;
var waypoints;
var distance = "<br>";
var routes;

// Attach your callback function to the `window` object
window.initialize = function() {
  initMap();
  for(let i = 0; i < inputs.length; i++)
  {
  addAutoComplete(inputs[i]);
  }
  searchLoc("id_starting_from");
  searchLoc("id_ending_at", searchStops);
  
  
}

function searchStops() {
  createWaypoint(0);
}
function initMap() {
  // JS API is loaded and available
  
  
  waypoints = []
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 40.443, lng: -79.942 },
    zoom: 8,
  });

  var rendererOptions = {
    suppressMarkers: true,
  };

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer(rendererOptions);
  directionsRenderer.setMap(map);
    infoWindow2 = new google.maps.InfoWindow();
    infoWindow = new google.maps.InfoWindow();
    const locationButton = document.createElement("button");
    locationButton.textContent = "Go to Current Location";
    locationButton.classList.add("goto-location")
    locationButton.setAttribute("type", "button")
    map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(locationButton);
    locationButton.addEventListener("click", () => {
    if (navigator.geolocation) {
      console.log("yet!")
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          infoWindow.setPosition(pos);
          infoWindow.setContent("My current location")
          infoWindow.open(map);
          console.log("hiii")
          map.panTo(pos);
          map.setZoom(8);
        },
        () => {
          handleLocationError(true, infoWindow, map.getCenter());
        },
        {timeout: 10000}
      );
    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
      }
    });
}


function addAutoComplete(id) {
  const input = document.getElementById(id);
  const options = {
    fields: ["address_components", "geometry", "icon", "name"],
    strictBounds: false,
    type: 'geocode',
  };
  const autocomplete = new google.maps.places.Autocomplete(input, options);
}
function searchLoc(id, callback, response=null) {
    const input = document.getElementById(id);
    const q = input.value;
    request = {
        query: q,
        fields: ['name', 'geometry'],
    }

    let service = new google.maps.places.PlacesService(map);


    service.findPlaceFromQuery(request, function(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
      for (var i = 0; i < results.length; i++) {
        if(id == "id_starting_from" || id == "id_ending_at")
        {
          createEndpoint(results[i], id);
        }
        else{
          console.log(document.getElementById('id_start_date').value);
          let date_of_waypoint = new Date(document.getElementById('id_start_date').value);
          addWaypoint(results[i], date_of_waypoint, response);
          drawRoute();
        }
      }
      map.panTo(results[0].geometry.location);
      typeof callback === 'function' && callback();
    }
    else {
      displayError("No results found for location. Please try searching another location!")
    }
    });
}

function get_marker(waypoint) {
  return waypoint[0]
}
function get_datetime(waypoint) {
  return waypoint[1]
}
function get_id(waypoint) {
  return waypoint[2]
}

function createWaypoint(index) {
  if(index == stops.length) {
    console.log("eek")
    drawRoute();
  }
  else {
  request = {
      query: stops[index]['address'],
      fields: ['name', 'geometry'],
  }
  let start_date = stops[index]['start_date']
  let date_of_waypoint = new Date(start_date);

  let marker;
  let service = new google.maps.places.PlacesService(map);
  service.findPlaceFromQuery(request, function(results, status) {
  if (status === google.maps.places.PlacesServiceStatus.OK) {
      marker = new google.maps.Marker({
        map,
        position: results[0].geometry.location,
      });
      waypoints.push([marker, date_of_waypoint, stops[index]['id']]);
      addWaypointListener(index);
      createWaypoint(index + 1);
      
  }
  else {
    displayError("Stop location "+ index.toString() + " not found.")
  }
  });
}
}

function addStartInfo () {
  infoWindow.setPosition(startLoc.getPosition());
  infoWindow.setContent("Starting from: " + startLoc.getTitle() + '<br>' + distance || "");
  infoWindow.open(map);
  infoWindow2.open(null);
}

function addEndInfo () {
  infoWindow.setPosition(endLoc.getPosition());
  infoWindow.setPosition(endLoc.getPosition());
  if(endLoc.getPosition().lat() == startLoc.getPosition().lat()
    && endLoc.getPosition().lng() == startLoc.getPosition().lng()){
    infoWindow.setContent("Starting from and Ending at: " + endLoc.getTitle() + '<br>' + distance || "");
  }
  else {
    infoWindow.setContent("Ending at: " + endLoc.getTitle() + '<br>' + distance || "");
  }
  infoWindow.open(map);
  infoWindow2.open(null);
}
function calcDistance(dist){
  if(dist >= 1000){
    dist = (Math.floor(dist/100)) / 10
    return dist + " km";
  }
  return dist + " m";
}

function calcDuration(dur){
  if(dur >= 60){
    dur = Math.floor(dur / 60);
    if(dur >= 60){
      let minutes = dur % 60;
      dur = Math.floor(dur / 60);
      return dur + "h " + minutes + "m";
    }
    return dur + " min";
  }
  return dur + " sec";
}

function createEndpoint(place, id) {
  if (!place.geometry || !place.geometry.location) return;

    if (id=="id_starting_from") {
      if(startLoc != null)
        {
        startLoc.setPosition(place.geometry.location);
        startLoc.setTitle(place.name || "Couldn't find place name");
        }
      else 
        {
          console.log("start")
          startLoc = new google.maps.Marker({
            map,
            position: place.geometry.location,
          });
          startLoc.setTitle(place.name || "Couldn't find place name");
          google.maps.event.addListener(startLoc, "click", addStartInfo );
        }
    }
    else if (id=="id_ending_at") {
      if(endLoc != null)
        {
          endLoc.setPosition(place.geometry.location);
          endLoc.setTitle(place.name || "Couldn't find place name");
        }
      else
        {
          console.log("end")
          endLoc = new google.maps.Marker({
            map,
            position: place.geometry.location,
          });
          endLoc.setTitle(place.name || "Couldn't find place name");
          google.maps.event.addListener(endLoc, "click", addEndInfo );
        }

    }
  }

  function addWaypoint(place, date_of_waypoint, response) {
    if (!place.geometry || !place.geometry.location) return;
    const marker = new google.maps.Marker({
        map,
        position: place.geometry.location,
      });
      
      let loc_id = response['id']
      for(let i = 0; i < waypoints.length;  i++) {
        date1 = get_datetime(waypoints[i])
        if(date_of_waypoint < date1){
          waypoints.splice(i, 0, [marker, date_of_waypoint, loc_id]);
          addWaypointListener(i, response);
          return;
        }
      }
        waypoints.push([marker, date_of_waypoint, loc_id]);
        addWaypointListener(waypoints.length - 1, response);
        
    
  }


function deleteItemJQuery(id) {
    $.ajax({
        url: "/tripplanner/delete-stop/"+id,
        type: "POST",
        data: "csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: function(data) {
          $("#error").html("");
          deleteWaypoint(id)
          addStopForm();
        },
        error: updateError
    });
}


function getCSRFToken() {
  let cookies = document.cookie.split(";")
  for (let i = 0; i < cookies.length; i++) {
      let c = cookies[i].trim()
      if (c.startsWith("csrftoken=")) {
          return c.substring("csrftoken=".length, c.length)
      }
  }
  return "unknown";
}

function getStopJQuery(loc_id) {
  $.ajax({
    url: "/tripplanner/get-stop/"+loc_id,
    dataType : "json",
    success: function(response) {
      editStopForm(response);
    },
    error: updateError
  })
}

function addStopForm() {
  document.getElementById("post-waypoints").reset();
  $("#submit_button").html("Add to Map");
  document.getElementById("post-waypoints").action =  '/tripplanner/add-stops';
}

function editStopForm(response) {
  $("#id_address").val(response['address']);
  $("#id_start_date").val(response['start_date']);
  $("#id_end_date").val(response['end_date']);
  $("#id_notes").val(response['notes']);
  $("#submit_button").html("Save Stop Changes");
  document.getElementById("post-waypoints").action =  '/tripplanner/edit-stop/'+response['id'];
}

function editWaypoint(response) {
  console.log(response);
  infoWindow2.open(null);
  deleteMarker(response['id']);
  var frm = $('#post-waypoints');
  searchLoc('id_address',frm[0].reset.bind(frm[0]),response)
  addStopForm();
}
function deleteWaypoint(loc_id) {
  deleteMarker(loc_id);
  drawRoute();
  infoWindow2.open(null);
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')');
}

function displayError(message) {
    $("#error").html(message);
}
  
  
  function drawRoute(){
    if(startLoc && endLoc) {
      waypointLocs = waypoints.map(waypoint => 
                                      ({ location: waypoint[0].getPosition(), stopover: true}));
      
      var request = 
      {
        origin: startLoc.getPosition(),
        destination: endLoc.getPosition(),
        travelMode: 'DRIVING',
        waypoints: waypointLocs,
        provideRouteAlternatives: true,
        unitSystem: google.maps.UnitSystem.IMPERIAL
      }
      directionsService.route(request, function(response, status) {
        if (status == 'OK') {
          directionsRenderer.setDirections(response);
          routes = response.routes;
          let distance_temp = 0;
          let duration_temp = 0;
          for(let i = 0; i < routes[0].legs.length; i++)
          {
            let leg = routes[0].legs[i];
            for(let j = 0; j < leg.steps.length; j++){
              let step = leg.steps[j]
              distance_temp += step.distance.value
              duration_temp += step.duration.value
            }
          }
          distance = calcDistance(distance_temp) + "<br> Driving Time (no traffic): " + calcDuration(duration_temp);
        }
        else {
          displayError("Could not find route.")
        }
      });
    }
  }

// sets all markers to map
  function setMapOnAll(map) {
    for (let i = 0; i < waypoints.length; i++) {
      get_marker(waypoints[i]).setMap(map);
    }
  }

// hides markers, but keeps waypoints
  function clearMarkers() {
    setMapOnAll(null);
  }

// shows all markers in the array
  function showMarkers() {
    setMapOnAll(map);
  }

// deletes specific marker with loc_id
  function deleteMarker(loc_id) {
    console.log("hello: " + loc_id);
    for(let i = 0; i < waypoints.length; i++) {
      if(get_id(waypoints[i]) == loc_id) {
        get_marker(waypoints[i]).setMap(null);
        waypoints.splice(i, 1);
        return true;
      }
    }
    console.log("could not find marker to delete");
    return false;
  }



function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
      browserHasGeolocation
        ? "Error: The Geolocation service failed."
        : "Error: Your browser doesn't support geolocation."
    );
    infoWindow.open(map);
  }

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function formatDate(d) {
  if(d.getMinutes() < 10)
    return d.toLocaleDateString() + ", " + d.getHours() + ':0' + d.getMinutes();
  return d.toLocaleDateString() + ", " + d.getHours() + ':' + d.getMinutes();
}
function addWaypointListener(index, response=null) {
  let waypoint = waypoints[index]
  if(response != null) {
    
    response['start_date'] = formatDate(new Date(response['start_date']))
    response['end_date'] = formatDate(new Date(response['start_date']))
    google.maps.event.addListener(get_marker(waypoint), "click", () => {createStopInfoWindow(waypoint, response)});
  }
  else {
    response = stops[index];
    google.maps.event.addListener(get_marker(waypoint), "click", () => {createStopInfoWindow(waypoint, response)});
  }
  console.log(index);
  console.log(waypoints[index]);
}

function createStopInfoWindow(waypoint, response) {
    infoWindow2.setContent('Stop : '
                            + response['address']+'<br>'
                            +response['start_date'].toString()+ '<br>'
                            +" - " +response['end_date'].toString() + '<br> <br>'
                            +response['notes']+'<br> <br>'
                            + '<button onclick=getStopJQuery(' + get_id(waypoint) + ')> Edit </button>'
                            +'<button onclick=deleteItemJQuery(' + get_id(waypoint) + ')> Delete </button>')
    let pos = get_marker(waypoint).getPosition();
    infoWindow2.setPosition(pos);
    map.panTo(pos);
    infoWindow2.open(map);
    infoWindow.open(null);
  }
document.head.appendChild(script);
