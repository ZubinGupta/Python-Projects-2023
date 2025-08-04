#Name: Zubin Gupta
#Date: January 13, 2023
#For the Quarter Project I will be making a multiplayer turn-based combat game. 
#Block: D
import requests
import os
from sys import exit
from time import sleep
name = os.environ["REPL_OWNER"]
mult = (0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.4, 1.6, 1.8, 2)


def lonk(text):
    return "https://server.zubingupta.repl.co/" + text
    

def main():
    print(name + ", we need your help!")
    sleep(1)
    print("We need you to kill the evil monster!")
    sleep(1)
    play = ask("Will you help us, " + name + "? (y/n) ",
               ["y", "n"])
    print()
    if (play == "n"):
        exit(
            "The FitnessGram™ Pacer Test is a multistage aerobic capacity test that progressively gets more difficult as it continues. The 20 meter pacer test will begin in 30 seconds. Line up at the start. The running speed starts slowly, but gets faster each minute after you hear this signal. [beep] A single lap should be completed each time you hear this sound. [ding] Remember to run in a straight line, and run as long as possible. The second time you fail to complete a lap before the sound, your test is over. The test will begin on the word start. On your mark, get ready, start."
        )
    play = ask(
        "Would you like to create a new game, or join a game? (create/join) ",
        ["create", "join"])
    print()
    if (play == "create"):
        code = input("Enter a game code: ").strip(" ")
        while (requests.post(url=lonk("create"),
                             json={
                                 "key": code,
                                 "user": name
                             }).text == "error"):
            code = input("Code already exists! Enter another code: ").strip(
                " ")
        print("Code created!")
        setup(host=True, code=code)
    if (play == "join"):
        code = input("Enter a game code: ").strip(" ")
        req = requests.post(url=lonk("join"), json={
            "key": code,
            "user": name
        }).text
        print()
        while req != "success":
            if (req == "missing"):
                print("That game code does not exist.")
            if (req == "started"):
                print("That game has already started.")
            if (req == "rejoin"):
                print("You have already joined this game.")
            code = input("Enter another game code: ").strip(" ")
            req = requests.post(url=lonk("join"),
                                json={
                                    "key": code,
                                    "user": name
                                }).text
        print("Game joined successfully!")
        setup(host=False, code=code)


def ask(message, options):
    option = input(message)
    while option not in options:
        option = input("Please say one of these: " + str(options) + " ")
    return option


def players(code):
    req = get(code)
    print()
    if (req != "error"):
        arr = req.split(" ")
        arr.pop(0)
        print("Players in game with code", code + ":")
        for i in arr:
            print(i)
    else:
        print("Something wrong happened.")


def setup(host, code):
    if (host):
        print()
        print("What would you like to do?")
        print("Start Game (start)")
        print("View Players (view)")
        # TODO: Make kick function if time
        ans = ask("Enter your command: ", ["start", "view"])
        if (ans == "view"):
            players(code)
            setup(host, code)
        if ans == "start":
            players(code)
            prepare(code)
            start(code)
    if not host:
        players(code)
        repeat(code, get(code))


def repeat(code, line):
    req = get(code)
    if (req == line):
        repeat(code, req)
    elif (req[0] != "0"):
        print("Game started!")
        start(code)
    else:
        repeat(code, req)


def listify(str, sep):
    return (str.split(sep))


def get(code):
    return requests.post(url=lonk("stuf"), json={"key": code}).text


def prepare(code):
    requests.post(url=lonk("startgame"), json={"key": code})


def start(code):
    req = get(code)
    req = parse(req)
    display(req)
    handleio(code)


def handleio(code):
    prevturn = 0
    while requests.post(url=lonk("win"), json={"key": code}).text == "none":
        codeval = parse(get(code))
        turn, turntaker, req = codeval
        turntakernum, turntakername = turntaker
        if turn != prevturn:
            prevturn = turn
            print()
            display(codeval)
            if requests.post(url=lonk("win"), json={"key": code}).text != "none":
                break
            if turntakername == name:
                battleval = battle(turn, turntaker, req, code)
                print()
                display(battleval)
                requests.post(url=lonk("update"),
                              json={
                                  "key": code,
                                  "data": unparse(battleval)
                              })
    if requests.post(url=lonk("win"), json={"key": code}).text == "lose":
        print("You lose!")
    if requests.post(url=lonk("win"), json={"key": code}).text == "win":
        print("You win!")
        sleep(2)
        print("...")
        sleep(1)
        print("By the way, who said that we were the good guys! >:)")


def battle(turn, turntaker, req, code):
    badguy = req.pop(len(req) - 1)
    player = req[turntaker[0]]
    if player[1] < 0: player[1] = 0
    if player[1] == 0:
        print("You are dead. You can't do anything.")
    else:
        optionlist = ["Attack", "Raise Attack", "Raise Defense"]
        if player[2] >= 10: optionlist.remove("Raise Attack")
        if player[3] >= 10: optionlist.remove("Raise Defense")
        option = ask(
            "What would you like to do? \n Attack \n Raise Attack \n Raise Defense \n Enter here: ",
            optionlist)
        if option == "Attack":
            badguy[1] = badguy[1] - int(
                100 * mult[player[2]] / mult[badguy[3]])

        elif option == "Raise Attack":
            for i in range(len(req)):
                if req[i][2] < 10:
                    req[i][2] = req[i][2] + 1
            requests.post(url=lonk("turn"),
                          json={
                              "key": code,
                              "action": name + " raised everyone's attack!"})
        elif option == "Raise Defense":
            for i in range(len(req)):
                if req[i][3] < 10:
                    req[i][3] = req[i][3] + 1
            requests.post(url=lonk("turn"),
                          json={
                              "key": code,
                              "action": name + " raised everyone's defense!"
                          })
    req.append(badguy)
    return turn, turntaker, req


def unparse(data):
    turn, turntaker, req = data
    stringy = ""
    stringy += str(turn) + " " + str(turntaker[0])
    for item in req:
        stringy += " " + item[0] + " " + str(item[1]) + "," + str(
            item[2]) + "," + str(item[3])
    return stringy


def parse(data):
    req = data.split()
    turn = int(req[0])
    playernum = int(req[1])
    req.pop(0)
    req.pop(0)
    playername = ""
    players = []
    for i in range(0, len(req), 2):
        player = req[i]
        stats = req[i + 1]
        if i / 2 == playernum: playername = player
        stats = stats.split(",")
        for i in range(len(stats)):
            stats[i] = int(stats[i])
        stats.insert(0, player)
        players.append(stats)
    return turn, (playernum, playername), players


def display(req):
    turn, useless, tempreq = req
    print("Turn", turn)
    for item in tempreq:
        if item[0] == "evilbadguy": print("Kevin: ")
        else: print(item[0] + ":")
        print("HP:", item[1])
        print("Attack Multiplier:", mult[item[2]])
        print("Defense Multiplier:", mult[item[3]])


main()
