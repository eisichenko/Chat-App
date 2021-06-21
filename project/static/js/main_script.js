$(document).ready(function () {
    min_diff = 1e9
    min_href = undefined

    // highlighting navigation bar
    $('a').each(function (_, cur_ref) {
        cur_ref = cur_ref.href

        window_ref = window.location.href

        substr_start = window_ref.indexOf(cur_ref)

        if (substr_start >= 0)
        {
            substr_end = substr_start + cur_ref.length - 1

            cur_diff = window_ref.length - substr_end - 1
    
            if (min_diff > cur_diff && cur_diff >= 0) {
                min_href = this
                min_diff = cur_diff
            }
        }
    });

    $(min_href).closest("li").addClass("active");

    $('#message_text_area').focus()

    var socket = io.connect();

    var sent_msg = false

    $('#message_form').on('submit', function (e) {
        e.preventDefault()

        let msg = $('#message_text_area').val()

        if (msg && msg.length > 0)
        {
            socket.emit('send message', {
                message: msg
            })
    
            $('#message_text_area').val('').focus()
        }

        $('#message_text_area').focus()       
        
        sent_msg = true
    })

    socket.on('update messages', function (json) {

        $('#no-msg').remove()

        console.log(window.location.href)
        console.log(json.chat_id)

        href = window.location.href

        if (href.endsWith('/messages'))
        {
            console.log('messages')

            $('#unread_msg_chat' + json.chat_id).remove();

            $('#chat' + json.chat_id).append('<p id="unread_msg_chat' + json.chat_id +  '" class="unread-msg ms-3">' + json.current_unread + ' unread</p>')
        }
        else if (href.endsWith('/messages/chat/' + json.chat_id))
        {
            if (sent_msg)
            {
                var message_box = $('<div class="col-6 container user-message"></div>');

                var name_tag = $('<p class="pe-2 sender-name"></p>')

                name_tag.append(document.createTextNode(json.username + ': '))

                var msg_tag = $('<p style="display: inline;"></p>')

                msg_tag.append(document.createTextNode(json.message))

                message_box.append(name_tag)
                message_box.append(msg_tag)
                
                $('#chat').append(message_box)

                var time_tag = $('<p class="user-msg-time"></p>')
                time_tag.append(document.createTextNode(json.time))

                $('#chat').append(time_tag)
            }
            else
            {
                var message_box = $('<div class="col-6 container not-user-message"></div>');

                var online_tag = $('<p class="ps-1 pe-0 online" style="display: inline;">• </p>')

                var name_tag = $('<p class="pe-2 sender-name"></p>')

                name_tag.append(document.createTextNode(json.username + ':'))

                var msg_tag = $('<p style="display: inline;"></p>')

                msg_tag.append(document.createTextNode(json.message))

                message_box.append(online_tag)
                message_box.append(name_tag)
                message_box.append(msg_tag)
                
                $('#chat').append(message_box)

                var time_tag = $('<p class="not-user-msg-time"></p>')
                time_tag.append(document.createTextNode(json.time))

                $('#chat').append(time_tag)

                socket.emit('read', json)
            }
        }
        else
        {
            console.log('another page')
        }

        // scroll down to the end

        $('html, body').scrollTop( $('#chat').height() );

        sent_msg = false
    })

    if ($('#unread-msg').offset())
    {
        $('html, body').scrollTop($('#unread-msg').offset().top)
    }
    else
    {
        $('html, body').scrollTop($('#chat').height())
    }
    

    $('#message_text_area').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            event.preventDefault()
            $('#message_form').trigger('submit')
        }
    });
});
