function updateBtnText() {
    var btnText = $('#start-btn').text()
    var newBtnText = btnText;

    if ($('#start-btn').prop('disabled')) { // button was disabled
        if (btnText == "Start to Focus") {
            newBtnText = "Focusing"
        } else if (btnText == "Start your Break") {
            newBtnText = "Enjoy your Break"
        }
    } else { // button was enabled
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

function parseTime(time) {
    var min = parseInt(time / 60, 10)
    var sec = parseInt(time % 60, 10);

    min = min < 10 ? "0" + min : min;
    sec = sec < 10 ? "0" + sec : sec;

    $('#time').text(min + " : " + sec); // update timer
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

        if (timer-- < 1) {
            $('#start-btn').prop('disabled', false); // enable the button
            updateBtnText()
            setTimeout(() => { 
                parseTime(currentTime)
            }, 1000);
            clearInterval(refresh); // exit refresh loop

            var music = $("#alarm")[0];
            music.play();
        }
    }, 1000);
}

window.onload = function() { // show the timer on page load
    parseTime(focusTime);
}

function start() {
    $('#start-btn').prop('disabled', true); // disable the button on click
    jQuery(function ($) {
        startTimer(currentTime);
    })
}
