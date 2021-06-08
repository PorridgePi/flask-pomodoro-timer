import flask, json, re, os
from flask import render_template, request, url_for, redirect
from datetime import datetime

app = flask.Flask(__name__)

def openJSON():
    if os.path.exists("data.json"):
        with open("data.json", 'r') as f:
            try:
                db = json.load(f)
            except json.decoder.JSONDecodeError:
                os.remove("data.json") # could prompt for download next time before removing
                return render_template("error.html", error="JSON config file is corrupted.")
    else:
        db = {
            "settings": {
                "focusTime": 1500, # default focusTime = 25 minutes
                "breakTime": 300   # default breakTime = 5 minutes
            },
            "records": {

            }
        }

    return db

def saveJSON(db):
    with open('data.json', 'w') as f:
        json.dump(db, f, indent=4, sort_keys=True)

@app.route("/", methods=["POST", "GET"])
def root():
    data = request.form

    db = openJSON()

    focusTime = db["settings"]["focusTime"]
    breakTime = db["settings"]["breakTime"]

    if "time" in data: # custom time
        if "isParsed" in data: # time is parsed
            focusTime = data["time"]
        else: # time is not parsed, need validation
            time = data["time"]

            if re.match("\d+[smh]?$", time) is None: # use Regex to validate time inputted
                return render_template("error.html", error="Please enter a valid time. For example: 35, 45s, 15m, 1h.")
            else:
                if time[-1] not in "smh": # an integer only (represents seconds)
                    focusTime = int(time)
                else: # with units -> convert to seconds
                    multiplier = {"s": 1, "m": 60, "h": 3600}
                    focusTime = int(time[:-1]) * multiplier[time[-1]]
    else: # default time
        pass

    return render_template("index.html", focusTime=focusTime, breakTime=breakTime)

@app.route("/focusStart", methods=["POST"])
def focusStart():
    data = request.form
    focusTime = data["focusTime"]

    db = openJSON()

    currentTime = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    db["records"][currentTime] = focusTime

    saveJSON(db)
    return ('', 204)

@app.route("/<int:seconds>s")
@app.route("/<int:seconds>")
def seconds(seconds):
    return render_template("custom.html", seconds=seconds)

@app.route("/<int:seconds>m")
def minutes(seconds):
    return render_template("custom.html", seconds=seconds*60)

@app.route("/<int:seconds>h")
def hours(seconds):
    return render_template("custom.html", seconds=seconds*3600)

@app.route("/settings")
def settings():
    db = openJSON()

    for i in ["focusTime", "breakTime"]:
        min = db["settings"][i] // 60
        sec = db["settings"][i] % 60

        min = "0" + str(min) if min < 10 else str(min)
        sec = "0" + str(sec) if sec < 10 else str(sec)

        db["settings"][i] = min + ":" + sec

    return render_template("settings.html", focusTime=db["settings"]["focusTime"], breakTime=db["settings"]["breakTime"])

@app.route("/save-settings", methods=["POST"])
def saveSettings():
    data = dict(request.form)

    db = openJSON()

    for i in data:
        time = data[i]
        if time == "":
            data[i] = db["settings"][i]
        elif re.match("\d+[smh]?$", time) is None: # use Regex to validate time inputted
            return render_template("error.html", error="Please enter a valid time. For example: 35, 45s, 15m, 1h.")
        else:
            if time[-1] not in "smh": # an integer only (represents seconds)
                data[i] = int(time)
            else: # with units -> convert to seconds
                multiplier = {"s": 1, "m": 60, "h": 3600}
                data[i] = int(time[:-1])*multiplier[time[-1]]

    db["settings"]["focusTime"] = data["focusTime"]
    db["settings"]["breakTime"] = data["breakTime"]

    saveJSON(db)

    return redirect(url_for("settings"))

@app.route("/stats")
def stats():
    db = openJSON()

    records = db["records"]

    data = {}

    for key in records:
        date = key.split('-')[0]
        focusTime = int(records[key])

        if date not in data:
            data[date] = focusTime
        else:
            data[date] += focusTime

    labels = [key for key in data]
    values = [data[key] for key in data]

    return render_template("stats.html", labels=labels, values=values)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

app.run(host="0.0.0.0", port=8080, debug=True)
