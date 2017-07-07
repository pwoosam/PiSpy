$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var gmarkers = [];

    socket.on('connect', function() {
        console.log('Connected!');
    });
    socket.on('disconnect', function() {
        console.log('Disconnected');
    });
    socket.on('updatemap', function(data) {
        console.log('Updating position to ' + data.lat + ', ' + data.lng);
        var pos = new google.maps.LatLng(data.lat, data.lng);
        map.setCenter(pos);

        var marker = new google.maps.Marker({
            position: pos,
            title:"Current location"
        });

        if (gmarkers.length > 0) {
            for(i=0; i<gmarkers.length; i++) {
                gmarkers[i].setMap(null);
            }
        }
        gmarkers.push(marker);
        marker.setMap(map); 
    });
});
