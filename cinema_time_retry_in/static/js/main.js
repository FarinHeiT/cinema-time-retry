const createRoom = document.querySelector('#CreateRoom');

createRoom.addEventListener('submit', (e) => {
    e.preventDefault()
    let videoLink = document.querySelector('#videoLink').value;
    let password = document.querySelector('#password').value;
    let Name = document.querySelector('#Name').value;

    socket.emit('create_room', {
        videoLink, password, Name
    });
    return false
})

socket.on('error', (data)=>{
    createToast(data.title, data.content, "alert-danger")
})