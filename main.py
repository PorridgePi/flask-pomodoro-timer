import flask, json, re, os
from flask import render_template, request, url_for, redirect
from datetime import datetime

app = flask.Flask(__name__)

def openJSON(): # open a JSON file, check for corruption, and return a dictionary
    if os.path.exists("data.json"):
        with open("data.json", 'r') as f:
            try:
                db = json.load(f)
            except json.decoder.JSONDecodeError: # corrupted JSON
                os.remove("data.json") # in future, could prompt to download a backup version before removing 
                return render_template("error.html", error="JSON config file is corrupted.") # return error
    else: # no JSON file present, create empty dictionary
        db = {
            "settings": {
                "focusTime": 1500, # default focusTime = 25 minutes
                "breakTime": 300   # default breakTime = 5 minutes
            },
            "records": {

            }
        }

    return db

def saveJSON(db): # save a dictionary as a JSON file
    with open('data.json', 'w') as f:
        json.dump(db, f, indent=4, sort_keys=True)

@app.route("/", methods=["POST", "GET"]) # route for root
def root():
    data = request.form

    db = openJSON() # open current database

    focusTime = db["settings"]["focusTime"] # get focusTime in settings
    breakTime = db["settings"]["breakTime"] # get breakTime in settings

    if "time" in data: # custom time inputted
        if "isParsed" in data: # time is parsed correctly
            focusTime = data["time"] 
        else: # time is not parsed, need validation
            time = data["time"]

            if re.match("\d+[smh]?$", time) is None: # use Regex to validate time inputted
                return render_template("error.html", error="Please enter a valid time. For example: 35, 45s, 15m, 1h.") # time is invalid, return error
            else: # time is valid
                if time[-1] not in "smh": # only an integer is inputted (the integer represents seconds)
                    focusTime = int(time)
                else: # time has units -> convert to seconds
                    multiplier = {"s": 1, "m": 60, "h": 3600}
                    focusTime = int(time[:-1]) * multiplier[time[-1]]
    else: # use default time from settings
        pass

    return render_template("index.html", focusTime=focusTime, breakTime=breakTime)

@app.route("/focusStart", methods=["POST"]) # route that is requested when the Start to Focus button is pressed
def focusStart():
    data = request.form
    focusTime = data["focusTime"] # get the the focusTime of that session

    db = openJSON() # open current database

    currentTime = datetime.now().strftime("%Y%m%d-%H%M%S-%f") # get and format the current time

    db["records"][currentTime] = focusTime # add an record to the database with the currentTime as the key and the focusTime as the value

    saveJSON(db) # save the database into the JSON file
    return ('', 204) # return 204 No Content

@app.route("/<int:seconds>s") # route for custom time in seconds
@app.route("/<int:seconds>")
def seconds(seconds):
    return render_template("custom.html", seconds=seconds) # renders custom.html which will redirect back to root with the inputted time

@app.route("/<int:seconds>m") # route for custom time in minutes
def minutes(seconds):
    return render_template("custom.html", seconds=seconds*60) # renders custom.html which will redirect back to root with the inputted time

@app.route("/<int:seconds>h") # route for custom time in hours
def hours(seconds):
    return render_template("custom.html", seconds=seconds*3600) # renders custom.html which will redirect back to root with the inputted time

@app.route("/settings") # route for settings page
def settings():
    db = openJSON() # open current database

    for i in ["focusTime", "breakTime"]: # obtain the current settings for focusTime and breakTime and format it
        min = db["settings"][i] // 60
        sec = db["settings"][i] % 60

        min = "0" + str(min) if min < 10 else str(min)
        sec = "0" + str(sec) if sec < 10 else str(sec)

        db["settings"][i] = min + ":" + sec

    return render_template("settings.html", focusTime=db["settings"]["focusTime"], breakTime=db["settings"]["breakTime"])

@app.route("/save-settings", methods=["POST"]) # route to save settings
def saveSettings():
    data = dict(request.form)

    db = openJSON() # open current database

    for i in data: # two data - focusTime and breakTime
        time = data[i]
        if time == "": # blank response -> leave settings as it is
            data[i] = db["settings"][i] 
        elif re.match("\d+[smh]?$", time) is None: # use Regex to validate time inputted
            return render_template("error.html", error="Please enter a valid time. For example: 35, 45s, 15m, 1h.") # time is invalid, return error
        else: # time is valid
            if time[-1] not in "smh": # only an integer is inputted (the integer represents seconds)
                data[i] = int(time)
            else: # time has units -> convert to seconds
                multiplier = {"s": 1, "m": 60, "h": 3600}
                data[i] = int(time[:-1])*multiplier[time[-1]]

    # make changes to the database
    db["settings"]["focusTime"] = data["focusTime"]
    db["settings"]["breakTime"] = data["breakTime"]

    saveJSON(db) # save the database into the JSON file

    return redirect(url_for("settings"))

@app.route("/stats") # route for the stats page
def stats():
    db = openJSON() # open current database

    records = db["records"]

    data = {} # data obtained after manipulation of the records

    for key in records:
        date = key.split('-')[0] # get date
        focusTime = int(records[key]) # get focusTime

        # sum up the focusTime for each date
        if date not in data:
            data[date] = focusTime
        else:
            data[date] += focusTime

    labels = [key for key in data] # labels are the dates
    values = [data[key] for key in data] # values are the focusTime

    return render_template("stats.html", labels=labels, values=values)

@app.errorhandler(404) # route for 404 error
def page_not_found(error):
    return render_template("404.html"), 404

app.run(host="0.0.0.0", port=8080, debug=True)
