let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', () => {
    socket.emit('join_room', {'room_name': room_name})
});

socket.on('displaySayHi', () => {
    const state = player.getPlayerState();
    console.log(state)
    if(state == 2 | state == 5 || state == -1){
        player.playVideo();

    } else {
        player.pauseVideo();
    }
});

document.querySelector('#bn').addEventListener('click', () => {
    const nrn = document.querySelector('#rn').value
    socket.emit('new_room_name', {'room_name':room_name, 'name' : nrn})
})


document.querySelector('#banUser').addEventListener('click', () => {
    let banUsername = document.querySelector('#banUsername').value
    socket.emit('ban', {'user': banUsername})
});

document.querySelector('#sayHi').addEventListener('click', () => {
    socket.emit('sayHi', {'room': room_name})
});


// YT JS API initialization
const tag = document.createElement('script');
tag.id = 'js-yt-api';
tag.src = 'https://www.youtube.com/iframe_api';
const firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

let player;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player-yt', {
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

// Fire on player ready state
function onPlayerReady(event) {
    console.info("READY ME")
    document.getElementById('player-yt').style.borderColor = '#FF6D00';
}

// Change border color corresponding to the player state
function changeBorderColor(playerStatus) {
    var color;
    if (playerStatus == -1) {
        color = "#37474F"; // unstarted = gray
    } else if (playerStatus == 0) {
        color = "#FFFF00"; // ended = yellow
    } else if (playerStatus == 1) {
        color = "#33691E"; // playing = green
    } else if (playerStatus == 2) {
        color = "#DD2C00"; // paused = red
    } else if (playerStatus == 3) {
        color = "#AA00FF"; // buffering = purple
    } else if (playerStatus == 5) {
        color = "#FF6DOO"; // video cued = orange
    }
    if (color) {
        document.getElementById('player-yt').style.borderColor = color;
    }
}
function onPlayerStateChange(event) {
    changeBorderColor(event.data);
}
