# Team Boneless Ice - Ayham Alnasser, Tiffany Cao, Clement Chan, Kiran Vuksanaj
# SoftDev1 pd1
# P01 -- flask app, ocean getaways
# 2019-11-18

from flask import Flask, render_template, request, session
import json
import urllib

app = Flask(__name__)

app.secret_key = "water"
baseC = "USD"
destinationC = "EUR"
# DB_FILE = "data/travel.db"

# =================== Part 1: Database Accessing Functions ===================

def addCurrency(base, destination, rate, timestamp):
    db = sqlite3.connect(DB_FILE)  # open database
    c = db.cursor()
    # check to see if database already has this base-destination pair
    command = "SELECT rate FROM currency WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
    cur = c.execute(command)
    temp = cur.fetchone()
    if temp:
        if temp[0] != rate: # updates exchange rate if not equal
            command = "UPDATE currency SET rate = \"" + rate + "\" WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
            c.execute(command)
            db.commit()
            db.close()
            return "updated rate"
    # if no base-destination pair exists, enter the new entry into the database
    command = "INSERT INTO currency (base, destination, rate, timestamp) " \
              "VALUES (\"" + base + "\", \"" + destination + "\", \"" + rate + "\", \"" + timestamp + "\")"
    c.execute(command)  # store currency rate between a base country and the destination
    db.commit()
    db.close()
    return "done"


# ======================= Part 2: Routes =======================

@app.route("/")
def landing_page():
    return render_template("welcome.html")

@app.route("/currency")
def money():
    u = urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/" + baseC)
    response= u.read()
    data = json.loads(response)
    data = data['rates']['' + destinationC]
    # addCurrency(baseC, destinationC, data, timestamp)
    return render_template("currency.html", rate = data)

if __name__ == "__main__":
    app.debug = True
    app.run()
