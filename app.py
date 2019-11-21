# Team Boneless Ice - Ayham Alnasser, Tiffany Cao, Clement Chan, Kiran Vuksanaj
# SoftDev1 pd1
# P01 -- flask app, ocean getaways
# 2019-11-18

from flask import Flask, render_template, request, session, flash
import json
import urllib
import sqlite3

app = Flask(__name__)

app.secret_key = "water"

baseC = "NZD"
destinationC = "EUR"
DB_FILE = "data/travel.db"

# =================== Part 1: Database/Table Accessing Functions ===================

def checkCurrency(base, destination):
    db = sqlite3.connect(DB_FILE)  # open database
    c = db.cursor()
    # check to see if database already has this base-destination pair
    command = "SELECT rate, timestamp FROM currency WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
    cur = c.execute(command)
    temp = cur.fetchone()
    print("here is temp")
    print(temp)
    if temp:
        # if temp[0][1] < time:
        #     return "need update"
        # else:
        return temp[0]
    db.commit()
    db.close()
    return "pair not found"

def updateCurrency(base, destination, rate, timestamp):
    db = sqlite3.connect(DB_FILE)  # open database
    c = db.cursor()
    # check to see if database already has this base-destination pair
    command = "SELECT rate FROM currency WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
    cur = c.execute(command)
    temp = cur.fetchone()
    if temp:
        command = "UPDATE currency SET timestamp = \"" + timestamp + "\" WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
        c.execute(command)
        db.commit()
        if temp[0] != rate: # updates exchange rate if not equal
            command = "UPDATE currency SET rate = \"" + rate + "\" WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
            c.execute(command)
            db.commit()
            db.close()
            return "updated rate and time"
        else: return "updated time"
    # if no base-destination pair exists, enter the new entry into the database
    command = "INSERT INTO currency (base, destination, rate, timestamp) " \
              "VALUES (\"" + base + "\", \"" + destination + "\", \"" + rate + "\", \"" + timestamp + "\")"
    c.execute(command)  # store currency rate between a base country and the destination
    db.commit()
    db.close()
    return "added new pair"

dict = {}
file = open("weatherLinks.csv", "r") #opens second file with links
content = file.readlines() #parse through files by line
content = content[1:len(content)] #take out the table heading
for line in content:
    line = line.strip() #removes \n
    line = line.split(",") #if line does not contain quotes, split by comma
    dict[line[0]] = (line[1]) #key value pair
print(dict) #testing results
file.close()


# =================== Part 2: API Accessing Functions ===================

mapquest_key = "towBT1Gfo92PG6GjBcJs7NoIswGUtsaH"
mapquest_request = "http://open.mapquestapi.com/geocoding/v1/address?key={}&location={}"

def geolocate(city):
    city_encoded = city.replace(' ','%20')
    url = mapquest_request.format(mapquest_key,city_encoded)
    u = urllib.request.urlopen(url)
    response = u.read()
    data = json.loads(response)
    if data['info']['statuscode'] != 0:
        print("error arose while using Mapquest Geolocator")
        raise ValueError('Status code of {} while accessing Mapquest Geolocator: {}',data['info']['statuscode'],data['info']['messages'][0])
    result = data['results'][0]['locations'][0]
    out = {} # to nicely package only the results We Want, creating a new dictionary; makes it easier to get country code, etc.
    out['country'] = result['adminArea1']
    out['lat'] = result['latLng']['lat']
    out['lon'] = result['latLng']['lng']
    out['mapurl'] = result['mapUrl']
    return out


restcountries_request = "https://restcountries.eu/rest/v2/alpha/{}"

def country_info(country): # country code, 2 letters (would work w a three letter code too)
    url = restcountries_request.format(country)
    u = urllib.request.urlopen(url)
    print(urllib.request.getproxies()) # just curious
    response = u.read()
    data = json.loads(response)

    out = {} # again to nicely package only the results we want, makes other code cleaner!
    out['currency'] = data['currencies'][0]
    out['name'] = data['name']
    return out


# ======================= Part 3: Routes =======================

@app.route("/")
def landing_page():
    flash('Previous search successfully cleared. (not actually tho, not yet anyways)')
    # NOTE! this is my weird way of asking, when a user loads root (aka the search page) the old search should be cleared out right?
    # in the way i did some navbar stuff i assumed that like, when on '/' no city is in session yet and so other pages should be disabled
    # and i made the 'search' link change to 'new search' if you're viewing it on other pages ('/info','/weather',etc)
    # -KV

    flash('example error','error')
    print(request.url)
    return render_template("welcome.html")


@app.route("/city")
def process_city():
    cityname = request.args['city_name']
    session['destination'] = cityname
    # print(cityname)

    geoloc = geolocate(cityname) # get the country of the desired city
    session['desiredCountry'] = geoloc['country']

    # print(geoloc['country'])
    country = country_info(geoloc['country']) # get the information of the desired country
    session['desiredCurrency'] = country['currency'] # get the currency object for the country

    # print(country['name'])
    # print(country['currency']['code'])

    flash('Currency symbol: {}'.format(country['currency']['code']))

    return render_template("root.html") # temporary!


@app.route("/currency")
def money():
    check = checkCurrency(baseC, session['desiredCurrency']['code'])
    print(check)
    if check == "pair not found":
        u = urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/" + baseC)
        response= u.read()
        data = json.loads(response)
        data = data['rates'][session['desiredCurrency']['code']]
        updateCurrency(baseC, session['desiredCurrency']['code'], str(data), "00")
        flash('Data received live from <em>Exchange Rate API</em>')
    else:
        print(check)
        data = check
        flash('Data retreived from cache')
    return render_template("currency.html", basecurrency = {}, rate = data, cityname = session['destination'], targetcurrency = session['desiredCurrency'])
@app.route("/weather")
def forecast():
    lat = str(session['geoloc']['lat'])
    lon = str(session['geoloc']['lon'])
    u = urllib.request.urlopen("https://api.darksky.net/forecast/2f2c21d2abb590bc642111165f1aa3f4/" + lat + "," + lon)
    response= u.read()
    data = json.loads(response)
    week = genDic(data['daily']['data'])
    hours = genDic(data['hourly']['data'])
    return ""

def genDic(dic):
    li = ['icon','temperatureHigh','temperatureLow','windSpeed','precipProbability','precipType','temperature']
    newSet = []
    for i in range(0,len(dic)):
        newSet.append({})
        for idx in li:
            if (idx in dic[i]):
                newSet[i][idx] = dic[i][idx]
    return newSet


if __name__ == "__main__":
    app.debug = True
    app.run()
