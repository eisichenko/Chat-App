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

var username_field = document.getElementById("username")
var password_field = document.getElementById("password")

var username_verdict = document.getElementById("username_verdict")
var password_verdict = document.getElementById("password_verdict")

function validate() {

    if (!username_field)
    {
        username_verdict.style.visibility = 'hidden'
        return false
    }

    var username = username_field.value
    
    if (password_field)
    {
        var password = password_field.value
    }
    
    if (username)
    {
        if (username.length < 3 || username.length > 15)
        {
            username_verdict.classList.add('invalid')
            username_verdict.classList.remove('valid')

            if (username.length < 3)
            {
                username_verdict.innerHTML = 'Length is less than 3'
            }
            else
            {
                username_verdict.innerHTML = 'Length is more than 15'
            }

            var res_username = false
        }
        else
        {
            username_verdict.classList.add('valid')
            username_verdict.classList.remove('invalid')

            if (username.length == 15) {
                username_verdict.innerHTML = 'OK (max 15 characters)'
            }
            else {
                username_verdict.innerHTML = 'OK'
            }

            var res_username = true
        }

        username_verdict.style.visibility = 'visible'
    }
    else
    {
        username_verdict.style.visibility = 'hidden'

        var res_username = false
    }

    if (!password_field) return res_username

    if (password)
    {
        if (password.length < 3 || password.length > 80)
        {
            password_verdict.classList.add('invalid')
            password_verdict.classList.remove('valid')

            if (password.length < 3)
            {
                password_verdict.innerHTML = 'Length is less than 3'
            }
            else
            {
                password_verdict.innerHTML = 'Length is more than 80'
            }

            var res_password = false
        }
        else
        {
            password_verdict.classList.add('valid')
            password_verdict.classList.remove('invalid')

            if (password.length == 80) {
                password_verdict.innerHTML = 'OK (max 80 characters)'
            }
            else {
                password_verdict.innerHTML = 'OK'
            }

            var res_password = true
        }

        password_verdict.style.visibility = 'visible'
    }
    else
    {
        password_verdict.style.visibility = 'hidden'

        var res_password = false
    }

    return res_username && res_password
}

$('#submit').on('click', function(){
    return validate()
})
