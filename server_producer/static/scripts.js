const socket = io();

// send messages to server
function sendMessage() {
    var input = document.getElementById('message_input');
    var message = input.value;
    input.value = '';
    socket.emit('message', message);
};

// waiting and showing marquee
socket.on('calculating', function(calculating) {
    document.getElementById('messages_output').innerText = calculating;
});

// show results
socket.on('result', function(data) {
    document.getElementById('messages_output').innerText = data;
});