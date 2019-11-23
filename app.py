# Team Boneless Ice - Ayham Alnasser, Tiffany Cao, Clement Chan, Kiran Vuksanaj
# SoftDev1 pd1
# P01 -- flask app, ocean getaways
# 2019-11-18

from flask import Flask, render_template, request, session, flash, redirect, url_for
import json
import urllib
import sqlite3

app = Flask(__name__)

app.secret_key = 'water'

keyfile = open('keys.json')
keys = json.load(keyfile)

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
# print(dict) #testing results
file.close()

def getUrl(weather):
    return dict[weather]


# =================== Part 2: API Accessing Functions ===================

mapquest_key = keys['mapquest']
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
    if result['geocodeQuality'] == "COUNTRY":
        raise ValueError('Poor granularity result of MapQuest Geolocator on \"{}\": Check for typos'.format(city))
    out = {} # to nicely package only the results We Want, creating a new dictionary; makes it easier to get country code, etc.
    out['country'] = result['adminArea1']
    out['lat'] = result['latLng']['lat']
    out['lon'] = result['latLng']['lng']
    out['mapUrl'] = result['mapUrl']
    session['desiredLat'] = out['lat']
    session['desiredLon'] = out['lon']
    li = out['mapUrl'].split("=")
    dimensions = li[3].split("&")
    dimensions[0] = "500,500"
    li[3] = "&".join(dimensions)
    session['mapUrl'] = "=".join(li)
    return out


restcountries_request = "https://restcountries.eu/rest/v2/alpha/{}"

def country_info(country): # country code, 2 letters (would work w a three letter code too)
    url = restcountries_request.format(country)
    u = urllib.request.urlopen(url)
    #print(urllib.request.getproxies()) # just curious
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

    # alert users of missing keys if they are missing
    for service in keys:
        if keys[service] == 'YOUR_API_KEY_HERE':
            flash('key for {} is missing: see README.md for instructions on procuring a key and installing it to the app.'.format(service),'error')
    return render_template("welcome.html")


@app.route("/city")
def process_city():
    cityname = request.args['city_name']
    session['destination'] = cityname
    # print(cityname)
    try:
        geoloc = geolocate(cityname) # get the country of the desired city
        session['desiredCountry'] = geoloc['country']
        country = country_info(geoloc['country']) # get the information of the desired country
        # print(geoloc['country'])
        session['desiredCurrency'] = country['currency']['code'] # get the currency object for the country
        flash('Currency symbol: {}'.format(country['currency']['code']))

        return redirect(url_for("information")) # temporary!
    except ValueError as e:
        flash('Error while accessing information: {}'.format(e),'error')
        return redirect(url_for('landing_page'))

    # print(country['name'])
    # print(country['currency']['code'])


@app.route("/currency")
def money():
    check = checkCurrency(baseC, session['desiredCurrency'])
    print(check)
    if check == "pair not found":
        u = urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/" + baseC)
        response= u.read()
        data = json.loads(response)
        data = data['rates'][session['desiredCurrency']]
        updateCurrency(baseC, session['desiredCurrency'], str(data), "00")
        flash('Data received live from Currency Exchange Rate API')
    else:
        print(check)
        data = check
        flash('Data retreived from cache')
    input = request.args.get("inputval")
    if input is None:
        input = 1
        outcome = "Please input a value."
    else:
        outcome = "" + str(float(input) * data)
    return render_template("currency.html", basecurrency = baseC, rate = data, cityname = session['destination'], targetcurrency = session['desiredCurrency'], money = input, conversion = outcome)


@app.route("/weather")
def forecast():
    lat = str(session['desiredLat'])
    lon = str(session['desiredLon'])
    u = urllib.request.urlopen("https://api.darksky.net/forecast/" + keys['darksky'] + "/" + lat + "," + lon)
    response= u.read()
    data = json.loads(response)
    week = genDicWeek(data['daily']['data'])
    now = genDicNow(data['currently'])
    summaryD = data['hourly']['summary']
    summaryW = data['daily']['summary']
    # print(summaryD + "\n" + summaryW)
    print(lat + "," + lon)
    units = data['flags']['units']
    # print(week[0])
    # print(hours[0])
    url = getUrl(data['currently']['icon'])
    # print(data['hourly']['data'])
    return render_template("weather.html", cityname = session['destination'], summaryD = summaryD, summaryW = summaryW, week = week, length = len(week), hours = now, image = url, unit = units)

def genDicNow(dic):
    li = ['icon','temperatureHigh','temperatureLow', 'temperature','windSpeed', 'precipIntensity', 'precipProbability', 'precipType', 'cloudCover', 'humidity', 'summary']
    newSet = {}
    for key in dic:
        for idx in li:
            if (key == idx):
                newSet[idx] = dic[idx]
    return newSet

def genDicWeek(dic):
    li = ['icon','temperatureHigh','temperatureLow', 'temperature','windSpeed', 'precipIntensity', 'precipProbability', 'precipType', 'cloudCover', 'humidity', 'summary']
    newSet = []
    for i in range(0,len(dic)):
        newSet.append({})
        for idx in li:
            if (idx in dic[i]):
                newSet[i][idx] = dic[i][idx]
    return newSet


@app.route("/info")
def information():
    city = session['destination']
    city_encoded = city.replace(' ','%20')
    u = urllib.request.urlopen("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&utf8=&format=json".format(city_encoded))
    response = u.read()
    data = json.loads(response)
    page = data['query']['search'][0]
    page = page['pageid']
    title = data['query']['search'][0]['title']
    title_encoded = title.replace(' ','%20')
    u = urllib.request.urlopen("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&exintro&titles=" + title_encoded + "&format=json")
    response = u.read()
    data = json.loads(response)
    data = data['query']['pages'][str(page)]['extract']
    data = data.split('.')
    if len(data) > 10:
        data = data[0:9]
    return render_template("information.html", city = session['destination'], info = data, length = len(data))



@app.route("/map")
def displayMap():
    zAdjust = 0
    li = session['mapUrl'].split("=")
    zoom = li[6].split("&")
    if ("oldZoom" in request.args):
        if (request.args['oldZoom'] != "None"):
            oldZoom = int(request.args['oldZoom'])
            newZoom = oldZoom + zAdjust
        else:
            oldZoom = 12
    else:
        oldZoom = 12
    if ('zoom' in request.args):
        if (request.args['zoom'] == "Zoom In"):
            print("zoom in")
            if (int(oldZoom) < 19 ):
                zAdjust +=1
        else:
            print("zoom out")
            if (int(oldZoom) > 0):
                zAdjust -=1
                    
    newZoom = oldZoom + zAdjust
    print(str(oldZoom) + "," + str(newZoom))
    zoom[0] = str(newZoom)
    li[6] = "&".join(zoom)
    url = "=".join(li)
    print(url)
    return render_template("map.html", pic = url, newZoom = str(newZoom))


if __name__ == "__main__":
    app.debug = True
    app.run()
