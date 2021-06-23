function checkCookie()
{
    if (navigator.cookieEnabled) return true;

    document.cookie = "cookietest=1";
    var ret = document.cookie.indexOf("cookietest=") != -1;
    document.cookie = "cookietest=1; max-age=0";
    
    return ret;
}

if (!checkCookie())
{
    alert("This website requires cookies to function properly");
}

function getCookie(name) 
{
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

var socket = io.connect();

socket.on('setup connection', function(json) 
{
    var date = new Date();
    var currentTimeZoneOffsetInHours = date.getTimezoneOffset() / 60;

    document.cookie = 'timezoneOffset=' + currentTimeZoneOffsetInHours + "; max-age=" + (60 * 60 * 24 * 365)
})

function twoDigitInteger(num)
{
    return (num < 10) ? "0" + num : num;
}

function getCurrentTime() 
{
    var d = new Date();
    
    year = d.getFullYear()
    month = twoDigitInteger(d.getMonth())
    date = twoDigitInteger(d.getDate())
    hours = twoDigitInteger(d.getHours())
    minutes = twoDigitInteger(d.getMinutes())
    seconds = twoDigitInteger(d.getSeconds())

    return `${date}/${month}/${year} ${hours}:${minutes}:${seconds}`
}


function buildSenderMessage(msg, time) 
{
    $('#message_text_area').val('').focus()

    var message_box = $('<div class="col-6 container user-message"></div>');

    var name_tag = $('<p class="pe-2 sender-name"></p>')

    name_tag.append(document.createTextNode(getCookie('username') + ': '))

    var msg_tag = $('<p style="display: inline;"></p>')

    msg_tag.append(document.createTextNode(msg))

    message_box.append(name_tag)
    message_box.append(msg_tag)

    $('#chat').append(message_box)

    var time_tag = $('<p class="user-msg-time"></p>')

    time_tag.append(document.createTextNode(time))

    $('#chat').append(time_tag)
}

function buildOtherUserMessage(msg, time, username) 
{
    var message_box = $('<div class="col-6 container not-user-message"></div>');

    var online_tag = $('<p class="ps-1 pe-0 online" style="display: inline;">• </p>')

    var name_tag = $('<p class="pe-2 sender-name"></p>')

    name_tag.append(document.createTextNode(username + ':'))

    var msg_tag = $('<p style="display: inline;"></p>')

    msg_tag.append(document.createTextNode(msg))

    message_box.append(online_tag)
    message_box.append(name_tag)
    message_box.append(msg_tag)
    
    $('#chat').append(message_box)

    var time_tag = $('<p class="not-user-msg-time"></p>')
    time_tag.append(document.createTextNode(time))

    $('#chat').append(time_tag)
}


$(document).ready(function () 
{
    var min_diff = 1e9
    var min_href = undefined

    // highlighting navigation bar
    $('a').each(function (_, cur_ref) 
    {
        cur_ref = cur_ref.href

        window_ref = window.location.href

        substr_start = window_ref.indexOf(cur_ref)

        if (substr_start >= 0)
        {
            substr_end = substr_start + cur_ref.length - 1

            cur_diff = window_ref.length - substr_end - 1
    
            if (min_diff > cur_diff && cur_diff >= 0) 
            {
                min_href = this
                min_diff = cur_diff
            }
        }
    });

    $(min_href).closest("li").addClass("active");

    $('#message_text_area').focus()

    $('#message_form').on('submit', function (e) 
    {
        e.preventDefault()

        let msg = $('#message_text_area').val()

        if (msg && msg.length > 0) 
        {
            
            buildSenderMessage(msg, getCurrentTime())

            $('html, body').scrollTop( $('#chat').height() );

            socket.emit('send message', { message: msg })
        }

        $('#message_text_area').focus()
    })

    socket.on('update messages', function (json) 
    {
        $('#no-msg').remove()

        href = window.location.href

        if (href.endsWith('/messages'))
        {
            console.log('messages')

            $('#unread_msg_chat' + json.chat_id).remove();

            $('#chat' + json.chat_id).append('<p id="unread_msg_chat' + json.chat_id +  '" class="unread-msg ms-3">' + json.current_unread + ' unread</p>')
        }
        else if (href.endsWith('/messages/chat/' + json.chat_id))
        {
            if (json.username == localStorage['currentUsername']) 
            {
                buildSenderMessage(json.message, json.time)
            }
            else 
            {
                buildOtherUserMessage(json.message, json.time, json.username)
                socket.emit('read', json)
            }
        }
        else
        {
            console.log('another page')
        }

        // scroll down to the end

        $('html, body').scrollTop( $('#chat').height() );
    })

    if ($('#unread-msg').offset()) 
    {
        $('html, body').scrollTop($('#unread-msg').offset().top)
    }
    else 
    {
        $('html, body').scrollTop($('#chat').height())
    }
    
    var limit_verdict = document.getElementById("server_verdict")

    $('#message_text_area').keypress(function(event)
    {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13') 
        {
            event.preventDefault()
            $('#message_form').trigger('submit')
        }
    });

    $('#message_text_area').keyup(function(event)
    {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        
        if ($("#message_text_area").val().length >= 1000 && keycode != '8' && keycode != '46') 
        {
            event.preventDefault()
            limit_verdict.innerHTML = "Limit 1000 characters"
        }
        else if ($("#message_text_area").val().length >= 0 && $("#message_text_area").val().length < 1000)
        {
            limit_verdict.innerHTML = "<br>"
        }
    });
});
