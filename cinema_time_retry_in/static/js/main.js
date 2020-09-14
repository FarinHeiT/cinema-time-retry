let socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', () => {
    console.log('a user connected');
    socket.emit('connection', {'data': 'hEY'})
});

socket.on('disconnect', () => {
    console.log('user disconnected');
});

const createRoom = document.querySelector('button[name="createRoom"]');

createRoom.addEventListener('click', () => {
    let videoLink = document.querySelector('#videoLink').value;

    socket.emit('create_room', {
        videoLink
    });
});

socket.on('redirect', function (data) {
    window.location = data.url;
});