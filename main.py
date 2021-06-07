import flask
import json
import re
from flask import render_template, request

app = flask.Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def root():
    data = request.form

    focusTime = 25
    breakTime = 5

    if "time" in data: # custom time
        if "isParsed" in data: # time is parsed
            return render_template("index.html", focusTime=data["time"], breakTime=breakTime)
        else: # time is not parsed, need validation
            time = data["time"]

            if re.match("\d+[smh]?$", time) is None: # use Regex to validate time inputted
                return render_template("error.html", error="Please enter a valid time. For example: 35, 45s, 15m, 1h.")
            else:
                if time[-1] not in "smh": # an integer only (represents seconds)
                    return render_template("index.html", focusTime=int(time), breakTime=breakTime)
                else: # with units -> convert to seconds
                    multiplier = {"s": 1, "m": 60, "h": 3600}
                    return render_template("index.html", focusTime=int(time[:-1])*multiplier[time[-1]], breakTime=breakTime)
    else: # default time
        return render_template("index.html", focusTime=focusTime, breakTime=breakTime)

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
    return render_template("settings.html")

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

app.run(host="0.0.0.0", port=8080, debug=True)
