var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
var startTime = 0;

function addToAudioStream(audioChunk, sampleRate, duration) {
    const frames = sampleRate * duration;
    var audioBuffer = audioCtx.createBuffer(1, frames, sampleRate);
    audioBuffer.getChannelData(0).set(audioChunk);

    var source = audioCtx.createBufferSource();
    source.buffer = audioBuffer;
    source.start(0);
    source.connect(audioCtx.destination);

    startTime += duration;
}

$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log('Connected!');
    });
    socket.on('disconnect', function() {
        console.log('Disconnected');
    });
    socket.on('audio', function(audio_data) {
        console.log('updating audio');
        addToAudioStream(audio_data, 44100, 1);
    });
});
