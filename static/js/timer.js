function updateBtnText() {
    var btnText = $('#start-btn').text()
    var newBtnText = btnText;

    if ($('#start-btn').prop('disabled')) { // button was disabled previously
        if (btnText == "Start to Focus") {
            $.post('/focusStart', {"focusTime": focusTime});
            newBtnText = "Focusing"
        } else if (btnText == "Start your Break") {
            newBtnText = "Enjoy your Break"
        }
    } else { // button was enabled previously
        if (btnText == "Focusing") {
            currentTime = breakTime; // set next time to breakTime
            newBtnText = "Start your Break"
        } else if (btnText == "Enjoy your Break") {
            currentTime = focusTime; // set next time to focusTime
            newBtnText = "Start to Focus"
        }
    }
    $('#start-btn').html(newBtnText) // update button text
}

function parseTime(time) { // format the time to mm:ss format and update elements
    var min = parseInt(time / 60, 10)
    var sec = parseInt(time % 60, 10);

    min = min < 10 ? "0" + min : min;
    sec = sec < 10 ? "0" + sec : sec;

    $('#time').text(min + " : " + sec); // update timer text
    $("title").html(min + " : " + sec + " - Pomodoro Timer"); // update page title
}

function startTimer(duration) {
    var timer = duration;

    updateBtnText()
    parseTime(timer)
    timer--;

    var refresh = setInterval(function() {
        updateBtnText()
        parseTime(timer)

        if (timer-- < 1) { // time reached
            $('#start-btn').prop('disabled', false); // enable the button
            updateBtnText()
            setTimeout(() => { 
                parseTime(currentTime) // update to new time after 1s delay
            }, 1000);
            clearInterval(refresh); // exit refresh loop

            var music = $("#alarm")[0];
            music.play(); // play music
        }
    }, 1000);
}

window.onload = function() { // show the timer on page load
    parseTime(focusTime);
}

function start() { // called when button is clicked
    $('#start-btn').prop('disabled', true); // disable the button on click
    jQuery(function ($) {
        startTimer(currentTime);
    })
}
