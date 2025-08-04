from flask import Flask, request
from enemy import emeny, parse
import os
from PIL import Image

dicty = {}
recentmove = {}
win = {}
log = open("log.txt", "w")
folder = os.path.join('static', 'hi')
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = folder


@app.route("/")
def index():
    # img = Image.open("image.png")
    # img.show()
    return "well hello there"


@app.route("/turn", methods=["POST"])
def move():
    jason = request.get_json(force=True)
    recentmove[jason["key"]] = jason["action"]
    return jason["action"]


@app.route("/getturn", methods=["POST"])
def getmove():
    jason = request.get_json(force=True)
    return recentmove[jason["key"]]


@app.route("/test123")
def test123():
    log.write(request.get_namespace() + "\n")
    log.flush()


@app.route("/create", methods=["POST"])  #creating a game code
def create():
    jason = request.get_json(force=True)
    if jason["key"] in dicty:  #game code already created
        log.write(jason["user"] + " tried creating preexisting code \"" +
                  jason["key"] + "\"\n")
        log.flush()
        return "error"
    dicty[jason["key"]] = "0 " + jason["user"]
    log.write(jason["user"] + " created code \"" + jason["key"] + "\"\n")
    log.flush()
    return "Code created!"


@app.route("/join", methods=["POST"])
def join():  #joining a game code
    jason = request.get_json(force=True)
    if (jason["key"] not in dicty):  #game code not created
        log.write(jason["user"] +
                  " attempted to join nonexistent game with code \"" +
                  jason["key"] + "\"\n")
        log.flush()
        return "missing"
    if (dicty[jason["key"]][0] != "0"):  #game already started
        log.write(jason["user"] +
                  " attempted to join already started game with code \"" +
                  jason["key"] + "\"\n")
        log.flush()
        return "started"
    if (jason["user"] in dicty[jason["key"]].split()):  #joins multiple times
        log.write(jason["user"] +
                  " attempted to repeatedly join game with code \"" +
                  jason["key"] + "\"\n")
        log.flush()
        return "rejoin"
    log.write(jason["user"] + " joined game with code \"" + jason["key"] +
              "\"\n")
    log.flush()
    dicty[jason["key"]] += " " + jason["user"]
    return "success"


@app.route("/stuf", methods=["POST"])
def stuf():
    jason = request.get_json(force=True)
    return dicty[jason["key"]]


@app.route("/startgame", methods=["POST"])
def startgame():
    jason = request.get_json(force=True)
    win[jason['key']] = "none"
    log.write("Started game with code \"" + jason['key'] + "\"\n")
    tup = (dicty[jason['key']].split(" "))
    tup.pop(0)
    tup = tuple(tup)
    startval = "1 0 "

    for tupval in tup:
        startval += tupval + " 1000,5,5 "  #first num is hp, second is attack stage, third is defense stage
    startval += "evilbadguy " + str(
        (len(tup) *
         1000)) + ",5,5"  #evilbadguy has the health of all players combined
    dicty[jason["key"]] = startval
    log.write(startval)
    log.flush()
    return "success!"


@app.route("/update", methods=["POST"])
def update():
    jason = request.get_json(force=True)
    vals = jason["data"]
    useless1, useless2, req = parse(vals)
    badguy = req.pop(len(req) - 1)
    if badguy[1] <= 0:
        win[jason['key']] = "win"
    lose = True
    for player in req:
        if int(player[1]) > 0:
            lose = False
    if lose: win[jason['key']] = "lose"
    log.write(jason['key'] + vals + "/n")
    log.flush()
    vals = str(int(vals.split()[0]) + 1) + " " + str(int(vals.split()[1]) +
                                                     1) + " " + vals.split(
                                                         " ", 2)[2]
    if (vals.split()[int(vals.split()[1]) * 2 + 2] == "evilbadguy"):
        vals = emeny(vals)
    dicty[jason["key"]] = vals
    return vals


@app.route("/win", methods=["POST"])
def didwewin():
    jason = request.get_json(force=True)
    return win[jason['key']]


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)
