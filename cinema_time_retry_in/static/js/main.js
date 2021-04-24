let socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', () => {
    console.log('a user connected');
    socket.emit('connection', {'data': 'hEY'})
});

const createRoom = document.querySelector('button[name="createRoom"]');

createRoom.addEventListener('click', () => {
    let videoLink = document.querySelector('#videoLink').value;
    let password = document.querySelector('#password').value;
    let Name = document.querySelector('#Name').value;

    socket.emit('create_room', {
        videoLink, password, Name
    });
});

socket.on('redirect', function (data) {
    window.location = data.url;
});

// Modal window
window.onload = function () {
    const openRoomSettings = document.querySelector(".pure-button")
    const closeRoomSettings = document.querySelector(".modal-close")
    const overlay = document.querySelector('#modal-overlay')
    const checkbox = document.querySelector('#private-room-checkbox')
    const password = document.querySelector('#invisible')

    openRoomSettings.onclick = function () {
        const modal = document.querySelector('#room-settings')
        modal.classList.add('active')
        overlay.classList.add('active')


    }

    closeRoomSettings.onclick = function () {
        const modal = document.querySelector('#room-settings')
        modal.classList.remove('active')
        overlay.classList.remove('active')
    }

    overlay.onclick = function () {
        const modal = document.querySelector('#room-settings')
        modal.classList.remove('active')
        overlay.classList.remove('active')
    }

    checkbox.onclick = function () {
        if (checkbox.checked == true) {
            password.classList.add('active')
        } else {
            password.classList.remove('active')
        }
    }
}