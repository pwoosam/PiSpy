$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log('Connected!');
    });
    socket.on('disconnect', function() {
        console.log('Disconnected');
    });
    socket.on('frame', function(frame_data) {
        console.log('updating frame');
        html = '<img class="img-responsive" src="data:image/jpeg;base64, ' + frame_data + '">';
        $('#frame img').replaceWith(html);
    });
});
