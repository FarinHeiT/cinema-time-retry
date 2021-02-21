let socket = io.connect('http://' + document.domain + ':' + location.port);
let user_timings = {}
let sync = true
let admin_name = ""

socket.on('connect', () => {
    console.log("Joining room:", room_name)
    socket.emit('join_room', {'room_name': room_name})
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
            socket.emit('change_settings', {'parameter': 'admin_rules', 'value': admin_rules.checked, 'room_name': room_name})
        })
    }

    let sync_checkbox = document.querySelector("#sync")
    sync_checkbox.addEventListener('click', () => {
        if (sync_checkbox.checked) {
            sync = true
            player.seekTo(user_timings[admin_name])
        } else {
            sync = false
        }
    })
}

socket.on('send_new_settings', (data) => {
    settings = data
})

let block = false


function onPlayerStateChange(event) {
    changeBorderColor(event.data)
    let sync_checkbox = document.querySelector("#sync")

    // Sync new user with admin
    if (event.data == -1) {
        if (role == "Creator") {
            player.seekTo(user_timings[Object.keys(user_timings)[0]])
        } else {
            player.seekTo(user_timings[admin_name])
        }
        block = true
    }

    // Only send if the state is 1 || 2 and synchronization if enabled
    if ((event.data == 1 || event.data == 2) && sync_checkbox.checked) {

        // Send if the user is admin or if correspondent settings are set
        if ((role == "Creator" || !settings['admin_rules']) && block == false) {
            socket.emit('player_state_handle', {
                'room': room_name,
                'action': event.data == 1 ? 'play' : event.data == 2 ? "pause" : event.data,
                'current_time': player.getCurrentTime(),
                'username': name
            })
        }
        block = false
    }
}

socket.on('send_unpause', (data) => {
    let sync_checkbox = document.querySelector("#sync")

    if (name != data['initiator'] && sync_checkbox.checked) {
        block = true
        player.seekTo(data['current_time'])
        player.playVideo()
    }
})

socket.on('send_pause', (data) => {
    let sync_checkbox = document.querySelector("#sync")

    if (name != data['initiator'] && sync_checkbox.checked) {
        block = true
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

setInterval(function () {
    socket.emit('get_room_info', {"room_name": room_name, "timing": [name, player.getCurrentTime()]})
}, 1000)

socket.on('send_room_info', (data) => {
    [timing_username, timing] = data['timing']
    user_timings[timing_username] = timing

    let online_user_list = document.querySelector('#online-users')
    online_user_list.innerHTML = ""
    data['room_info']['online'].forEach((user_id) => {
        let username = data['room_info']['names'][user_id]
        online_user_list.innerHTML += '<li>' + username + toHHMMSS(user_timings[username]) +'</li>'
    })

    admin_name = data['room_info']['names'][data['room_info']['admin']]
})

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

let toHHMMSS = (secs) => {
    let sec_num = parseInt(secs, 10)
    let hours   = Math.floor(sec_num / 3600)
    let minutes = Math.floor(sec_num / 60) % 60
    let seconds = sec_num % 60

    return [hours,minutes,seconds]
        .map(v => v < 10 ? "0" + v : v)
        .filter((v,i) => v !== "00" || i > 0)
        .join(":")
}