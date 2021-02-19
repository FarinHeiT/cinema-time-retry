let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', () => {
    console.log("Joining room:", room_name)
    socket.emit('join_room', {'room_name': room_name})
});

socket.on('displaySayHi', () => {
    const state = player.getPlayerState();
    console.log(state)
    if (state == 2 || state == 5 || state == -1) {
        player.playVideo();

    } else {
        player.pauseVideo();
    }
});

document.querySelector('#bn').addEventListener('click', () => {
    const nrn = document.querySelector('#rn').value
    socket.emit('new_room_name', {'room_name': room_name, 'name': nrn})
})


document.querySelector('#banUser').addEventListener('click', () => {
    let banUsername = document.querySelector('#banUsername').value
    socket.emit('ban', {'user': banUsername})
});


// Chat
socket.on('connect', function () {
    var form = $('form').on('submit', function (e) {
        e.preventDefault()
        let user_input = encodeURIComponent($('input.message').val());
        socket.emit('message', {
            'msg': user_input,
            'username': 'lolol'
        });

        // empty the input field
        $('input.message').val('').focus()
    })
})

socket.on("get_message", function (datam) {
    console.log("got message")
    console.log("message is defined")
    $('div.message_box').append('<div class="message_bbl"><p>' + datam.username + '</p> <p>' + datam.msg + '</p></div><br/>')
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

window.onload  = function() {
    let admin_rules = document.querySelector('#admin-rules')
    if (admin_rules) {
        admin_rules.addEventListener('click', () => {
            console.log("Trying to change settings")
            socket.emit('change_settings', {'parameter': 'admin_rules', 'value': admin_rules.checked, 'room_name': room_name})
        })
    }
}

socket.on('send_new_settings', (data) => {
    console.log('Got new settings')
    settings = data
})

function onPlayerStateChange(event) {
    console.info(event)
    changeBorderColor(event.data);
    console.log('Mine role', role, "\nNew player state:", event.data)
    if (role == "Creator" || !settings['admin_rules']) {
        socket.emit('player_state_handle', {
            'room': room_name,
            'action': event.data == 1 ? 'play' : event.data == 2 ? "pause" : event.data,
            'current_time': player.getCurrentTime(),
            'username': name
        })
    }

}

socket.on('send_unpause', (data) => {
    console.log('initiator', data['initiator'], "\nmine name", name)
    if (name != data['initiator']) {
        player.seekTo(data['current_time'])
        console.log('seeking')
        player.playVideo()
    }
})

socket.on('send_pause', (data) => {
    console.log('initiator', data['initiator'], "\nmine name", name)
    console.log('initiator', data['initiator'])
    if (name != data['initiator']) {
        player.pauseVideo()
        player.seekTo(data['current_time'])
    }
})

// TODO Cant locate progressbar because its inside of the iframe. Need to think of alternative
// let progressbar = document.querySelector(".ytp-progress-bar-container")
//
// progressbar.addEventListener('click', () => {
//     player.pauseVideo()
//
//     socket.emit('player_state_handle', {
//         'room': room_name,
//         'action': 'pause',
//         'current_time': player.getCurrentTime(),
//         'username': name
//     })
// })

// Instant disconnect on refresh\tab close
window.onbeforeunload = function () {
    socket.disconnect()
    return ''
}

// Send ping_online signal to the server every 10 sec
setInterval(function () {
    fetch('/room/' + room_name + '/ping_online')
        .then(response => response.json())
        .then(data => console.log('Ping online response: ', data))
}, 10000)