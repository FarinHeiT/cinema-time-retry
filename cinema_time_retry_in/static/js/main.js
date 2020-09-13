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
    let videoLink = document.querySelector('input[name="videoLink"]');

    console.log(generateRoomName());

    socket.emit('create_room', {
        videoLink
    });
});

function generateRoomName() {
    const link = "https://random-word-api.herokuapp.com/word?number=2&swear=0";

    axios.get(link)
        .then((response) => {
            [firstWord, secondWord] = response.data;
            console.log(firstWord +
                "-" +
                secondWord +
                Math.floor(Math.random() * (100 - 0) + 0));
        });
}
