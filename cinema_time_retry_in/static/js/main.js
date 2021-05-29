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

setInterval(function () {
    socket.emit("get_rooms_data")
}, 10000)

socket.on("new_room_data", (data)=>{
    console.log(data)
    data = JSON.parse(data)
    $('#example').DataTable( {
        bSort: false,
        data: data,
        columns: [
            { title: "Name" },
            { title: "Link" }
        ]
    } );
})