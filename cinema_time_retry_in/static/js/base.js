let socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', () => {
    console.log('a user connected');
    socket.emit('connection', {'data': 'hEY'})
});

 function createToast( title, content,  type){
      halfmoon.initStickyAlert({
      content: content,
      title: title,     
      alertType: type,   
      hasDismissButton: true, 
      timeShown: 5000             
    })
}

socket.on('redirect', function (data) {
    window.location = data.url;
})

function toogleDarkmode() {
    halfmoon.toggleDarkMode();
}