// Create the script tag, set the appropriate attributes
var script = document.createElement('script');
script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCtalreLvZ_sS089Vy_UtXyjXOX_sjbxHQ&callback=initMap&libraries=&libraries=geometry,places&v=weekly"


var map, infoWindow, directionsService, directionsRenderer;
var startLoc, endLoc, waypoints;

waypoints = []

// Attach your callback function to the `window` object
window.initMap = function() {
  // JS API is loaded and available
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

    infoWindow = new google.maps.InfoWindow();
    const locationButton = document.createElement("button");
    locationButton.textContent = "Go to Current Location";
    locationButton.classList.add("goto-location")
    locationButton.setAttribute("type", "button")
    map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(locationButton);
    locationButton.addEventListener("click", () => {
    console.log("pressed")
    if (navigator.geolocation) {
      console.log('hi')
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
          console.log("no location")
          handleLocationError(true, infoWindow, map.getCenter());
        },
        {timeout: 10000}
      );
    } else {
      // Browser doesn't support Geolocation
      console.log("no geolocation")
      handleLocationError(false, infoWindow, map.getCenter());
      }
    });
    for(let i = 0; i < inputs.length; i++)
      addAutoComplete(inputs[i]);

    if(document.getElementById("id_starting_from").value &&
    document.getElementById("id_ending_at").value){
      searchLoc("id_starting_from");
      searchLoc("id_ending_at");
    }
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
function searchLoc(id) {
    const input = document.getElementById(id);
    const q = input.value;
    request = {
        query: q,
        fields: ['name', 'geometry'],
    }

    var service = new google.maps.places.PlacesService(map);

    service.findPlaceFromQuery(request, function(results, status) {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
      for (var i = 0; i < results.length; i++) {
        if(id == "id_starting_from" || id == "id_ending_at")
          createMarker(results[i], id);
        else
          addWaypoint(results[i]);
      }
      drawRoute();
      map.panTo(results[0].geometry.location);
    }
    });
}

function searchByPlace(q) {
  request = {
      query: q,
      fields: ['name', 'geometry'],
  }

  var service = new google.maps.places.PlacesService(map);
  print(q)
  service.findPlaceFromQuery(request, function(results, status) {
  if (status === google.maps.places.PlacesServiceStatus.OK) {
    for (var i = 0; i < results.length; i++) {
        addWaypoint(results[i]);
    }
    drawRoute();
    map.panTo(results[0].geometry.location);
  }
  });
}

function createMarker(place, id) {
  if (!place.geometry || !place.geometry.location) return;

    if (id=="id_starting_from") {
      if(startLoc != null)
        {
        startLoc.setPosition(place.geometry.location);
        }
      else 
        {
          startLoc = new google.maps.Marker({
            map,
            position: place.geometry.location,
          });
          google.maps.event.addListener(startLoc, "click", () => {
            infoWindow.setPosition(place.geometry.location);
            infoWindow.setContent(place.name || "");
            infoWindow.open(map);
          });
        }
    }
    else if (id=="id_ending_at") {
      if(endLoc != null)
        {
          endLoc.setPosition(place.geometry.location);
        }
      else
        {
          endLoc = new google.maps.Marker({
            map,
            position: place.geometry.location,
          });
          google.maps.event.addListener(endLoc, "click", () => {
            infoWindow.setPosition(place.geometry.location);
            infoWindow.setContent(place.name || "");
            infoWindow.open(map);
          });
        }

    }
    else {
      const marker = new google.maps.Marker({
        map,
        position: place.geometry.location,
      });
      google.maps.event.addListener(marker, "click", () => {
        infoWindow.setPosition(place.geometry.location);
        infoWindow.setContent(place.name || "");
        infoWindow.open(map);
      });
      waypoints.push(marker);
    }

    

  }

  function addWaypoint(place) {
    if (!place.geometry || !place.geometry.location) return;
    const marker = new google.maps.Marker({
        map,
        position: place.geometry.location,
      });
      google.maps.event.addListener(marker, "click", () => {
        infoWindow.setPosition(place.geometry.location);
        infoWindow.setContent(place.name || "");
        infoWindow.open(map);
      });

      for(let i = 0; i < waypoints.length;  i++) {
        date1 = new Date()
      }
      waypoints.push(marker);
    
  }
  
  

  function drawRoute(){
    if(startLoc && endLoc) {
      waypointLocs = waypoints.map(marker => 
                                      ({ location: marker.getPosition(), stopover: true}));
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
        }
      });
    }
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

document.body.appendChild(script)