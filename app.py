# Team Boneless Ice - Ayham Alnasser, Tiffany Cao, Clement Chan, Kiran Vuksanaj
# SoftDev1 pd1
# P01 -- flask app, ocean getaways
# 2019-11-18

from flask import Flask, render_template, request, session, flash, redirect, url_for
import json
import urllib
import sqlite3
from datetime import date

app = Flask(__name__)

app.secret_key = 'water'

keyfile = open('keys.json')
keys = json.load(keyfile)

destinationC = "EUR"
DB_FILE = "data/travel.db"


# =================== Part 1: Database/Table Accessing Functions ===================

mapquest_staticmap_request = "https://www.mapquestapi.com/staticmap/v5/map?key={}&center={},{}&size=720,405&zoom={}"

def cachemap(url):
    # TODO: yeet

def checkCurrency(base, destination):
    if base == destination:
        return 1.0
    db = sqlite3.connect(DB_FILE)  # open database
    c = db.cursor()
    # check to see if database already has this base-destination pair
    command = "SELECT rate, timestamp FROM currency WHERE base = \"" + base + "\" AND destination = \"" + destination + "\""
    cur = c.execute(command)
    temp = cur.fetchone()
    # print("here is temp")
    # print(temp)
    if temp:
        if temp[1] != str(date.today()):
            return "need update"
        else:
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
        # print("here is temp2")
        # print(temp[0])
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

currencies = []
u = urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/USD")
response = u.read()
data = json.loads(response)
for key in data['rates']:
    currencies.append(key)

# print(currencies)
# print(len(currencies))

def getUrl(weather):
    return dict[weather]

# command = "CREATE TABLE IF NOT EXISTS place_info (countrycode TEXT, city TEXT PRIMARY KEY, currency TEXT, info TEXT, last_cached TIMESTAMP)"


def cachecity(cityname): # checks whether city is in database, updates/creates as necessary, adds city to session
    page,title = get_citypage(cityname)
    session['destination'] = title
    session['page'] = page
    # cityname = cityname.lower() # in order to standardize city inputs
    db = sqlite3.connect(DB_FILE)  # open database
    c = db.cursor()
    # print(cityname)
    # check to see if database already has this base-destination pair
    command = "select city,last_cached from place_info where city = '{}';".format(title)
    cur = c.execute(command)
    city_lastcache = cur.fetchone()
    print(title)
    print(city_lastcache)
    db.commit()
    db.close()
    if city_lastcache:
        if city_lastcache[1] != str(date.today()):
            flash('Data received live, updating cache')
            # case: database needs to be updated
            downloadcitydata(title)
            storesession(False)
        else:
            # case: database is up to date
            flash('Data received from cached database')
            loadcitydata_tosession(title)
    else:
        flash('First search for {}: Data downloaded live'.format(title))
        print('New thing')
        downloadcitydata(title)
        storesession(True)

def storesession(is_newcity):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    if is_newcity:
        command = "insert into place_info(city) values('{}')".format(session['destination'])
        c.execute(command)
    command = """
update place_info
    set
        currency = '{}',
        info = '{}',
        countrycode = '{}',
        last_cached = '{}',
        latitude = {},
        longitude = {},
        images = '{}'
    where
        city = '{}'
"""
    print(','.join(session['images']))
    print(session['info'])
    command = command.format(session['desiredCurrency'],session['info'].replace("'","''"),session['desiredCountry'],date.today(),session['desiredLat'],session['desiredLon'],','.join(session['images']),session['destination'])
    print(command)
    c.execute(command)
    db.commit()
    db.close()

def loadcitydata_tosession(cityname):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "select city,countrycode,currency,info,latitude,longitude,images from place_info where city = '{}'".format(cityname)
    c.execute(command)
    data = c.fetchone()
    session['destination'] = data[0]
    session['desiredCountry'] = data[1]
    session['desiredCurrency'] = data[2]
    session['info'] = data[3]
    session['desiredLat'] = data[4]
    session['desiredLon'] = data[5]
    session['images'] = data[6].split(',')
# =================== Part 2: API Accessing Functions ===================

mapquest_key = keys['mapquest'] # retreving key from json file
mapquest_request = "http://open.mapquestapi.com/geocoding/v1/address?key={}&location={}"


# function that uses the MapQuest API to find the country, coordinates, and map url of a given city
def geolocate(city):
    city_encoded = city.replace(' ','%20')
    url = mapquest_request.format(mapquest_key,city_encoded)
    u = urllib.request.urlopen(url)
    response = u.read()
    data = json.loads(response)
    if data['info']['statuscode'] != 0:
        # print("Error arose while using MapQuest Geolocator")
        raise ValueError('Status code of {} while accessing Mapquest Geolocator: {}',data['info']['statuscode'],data['info']['messages'][0])
    result = data['results'][0]['locations'][0]
    if result['geocodeQuality'] == "COUNTRY":
        raise ValueError('Poor granularity result of MapQuest Geolocator on \"{}\": Check for typos'.format(city))
    out = {} # to nicely package only the results We Want, creating a new dictionary; makes it easier to get country code, etc.
    out['country'] = result['adminArea1']
    out['lat'] = result['latLng']['lat']
    out['lon'] = result['latLng']['lng']
    out['mapUrl'] = result['mapUrl']
    li = out['mapUrl'].split("=")
    dimensions = li[3].split("&")
    dimensions[0] = "500,500"
    li[3] = "&".join(dimensions)
    out['mapUrl'] = "=".join(li)
    return out

def getMapUrl(lat,lon,newZoom):
    url = mapquest_staticmap_request.format(mapquest_key,lat,lon,newZoom)
    # print(url)
    return url

def calcZoom(args):
    zAdjust = 0
    if ("oldZoom" in args):
        if (args['oldZoom'] != "None"):
            oldZoom = int(args['oldZoom'])
            newZoom = oldZoom + zAdjust
        else:
            oldZoom = 12
    else:
        oldZoom = 12
    if ('zoom' in args):
        if (args['zoom'] == "Zoom In"):
           #  print("zoom in")
            if (int(oldZoom) < 19 ):
                zAdjust +=1
        else:
            # print("zoom out")
            if (int(oldZoom) > 0):
                zAdjust -=1
    # process zooming of map
    newZoom = oldZoom + zAdjust
   #  print(str(oldZoom) + "," + str(newZoom))
    return newZoom

restcountries_request = "https://restcountries.eu/rest/v2/alpha/{}"


# function that uses the REST Countries API to find the currency symbol given the country
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

ipstack_request = "http://api.ipstack.com/check?access_key={}"
ipstack_key = keys['ipstack']


def base_currency():
    url = ipstack_request.format(ipstack_key)
    u = urllib.request.urlopen(url)
    response = u.read()
    data = json.loads(response)
    return country_info(data["country_code"])


wikipedia_request1 = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&utf8=&format=json"
wikipedia_request2 = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&exintro&titles={}&format=json"
def get_citypage(city):
    city_encoded = city.replace(' ','%20')
    u = urllib.request.urlopen(wikipedia_request1.format(city_encoded))
    response = u.read()
    data = json.loads(response)
    page = data['query']['search'][0]  # get page ID of the Wikipedia page
    page = page['pageid']
    title = data['query']['search'][0]['title']  # get Wikipedia page title
    # session['destination'] = title
    return page,title
def get_citydata(title,page):
    title_encoded = title.replace(' ','%20')
    u = urllib.request.urlopen(wikipedia_request2.format(title_encoded))
    response = u.read()
    data = json.loads(response)
    data = data['query']['pages'][str(page)]['extract']
    data = data.split('. ')
    if len(data) > 10:  # cut down length of text
        data = data[0:9]
    return '. '.join(data)


def downloadcitydata(cityname): # compilation of all downloads that happen at /city
    info = get_citydata(session['destination'],session['page'])
    print('getting images')
    images = img_stuffs(session['destination'],session['page'])
    session['info'] = info
    session['images'] = images
    print(images)
    print(session['images'])
    geoloc = geolocate(cityname) # get the country of the desired city
    session['desiredLat'] = geoloc['lat']
    session['desiredLon'] = geoloc['lon']
    session['desiredCountry'] = geoloc['country']
    session['mapUrl'] = geoloc['mapUrl']
    country = country_info(geoloc['country']) # get the information of the desired country
    # print(geoloc['country'])
    session['desiredCurrency'] = country['currency']['code'] # get the currency object for the country
    flash('Currency symbol: {}'.format(country['currency']['code']))

# ======================= Part 3: Routes =======================

# landing route
@app.route("/")
def landing_page():
    # print(session['destination'])
    session.clear()
    flash('Previous search successfully cleared.')

    # alert users of missing keys if they are missing
    for service in keys:
        if keys[service] == 'YOUR_API_KEY_HERE':
            flash('Key for {} is missing: see README.md for instructions on procuring a key and installing it to the app.'.format(service),'error')
    return render_template("welcome.html")


# processes input from the Search box and redirects to information route
@app.route("/city")
def process_city():
    if request.args.get('city_name') is None:
        return redirect(url_for('landing_page'))
    cityname = request.args['city_name']
    try:
        cachecity(cityname)
        return redirect(url_for('information'))
    except ValueError as e:
        session.clear() # clear previous session
        flash('Error while accessing information: {}'.format(e),'error') # check if spelling of input is correct
        return redirect(url_for('landing_page'))

    # print(country['name'])
    # print(country['currency']['code'])

# uses Currency API to obtain currency exchange rates based on session['destination']
@app.route("/currency")
def money():
    baseC = base_currency()['currency']['code']
    if session.get('destination') is None:
        return redirect(url_for('landing_page'))
    check = checkCurrency(baseC, session['desiredCurrency']) # check if the base-destination pair is in database
    # print(check)
    if check == "need update" or check == "pair not found": # if the rate doesn't exist or needs to be updated
        u = urllib.request.urlopen("https://api.exchangerate-api.com/v4/latest/" + baseC)
        response= u.read()
        data = json.loads(response)
        data = data['rates'][session['desiredCurrency']]
        updateCurrency(baseC, session['desiredCurrency'], str(data), str(date.today()))
        flash('Data received live from Currency Exchange Rate API')
    else: # otherwise, return the rate
        data = check
        flash('Data retreived from cache')
    # calculator functioning
    input = request.args.get("inputval")
    if input is None:
        input = 1
        outcome = "Please input a value."
    else:
        outcome = "" + str(float(input) * data)
    return render_template("currency.html", basecurrency = baseC, rate = data, cityname = session['destination'], targetcurrency = session['desiredCurrency'], money = input, conversion = outcome, allcurrencies = currencies)


# uses Dark Sky API and the city's coordinates to obtain weather information
@app.route("/weather")
def forecast():
    if session.get('destination') is None:
        return redirect(url_for('landing_page'))
    lat = str(session['desiredLat']) # get the coordinates
    lon = str(session['desiredLon'])
    u = urllib.request.urlopen("https://api.darksky.net/forecast/" + keys['darksky'] + "/" + lat + "," + lon)
    response= u.read()
    data = json.loads(response)
    week = genDicWeek(data['daily']['data']) # get data for the week's forecast
    now = genDicNow(data['currently']) # get data for current forecast
    summaryD = data['hourly']['summary']
    summaryW = data['daily']['summary']
    # print(summaryD + "\n" + summaryW)
    print(lat + "," + lon)
    units = data['flags']['units'] # find the units
    # print(week[0])
    # print(hours[0])
    url = getUrl(data['currently']['icon']) # get the corresponding image icon from dictionary
    # print(data['hourly']['data'])
    return render_template("weather.html", cityname = session['destination'], summaryD = summaryD, summaryW = summaryW, week = week, length = len(week), hours = now, image = url, unit = units)

# nice packaging of API info
def genDicNow(dic):
    li = ['icon','temperatureHigh','temperatureLow', 'temperature','windSpeed', 'precipIntensity', 'precipProbability', 'precipType', 'cloudCover', 'humidity', 'summary']
    newSet = {}
    for key in dic:
        for idx in li:
            if (key == idx):
                newSet[idx] = dic[idx]
    return newSet

# nice packaging of API info
def genDicWeek(dic):
    li = ['icon','temperatureHigh','temperatureLow', 'temperature','windSpeed', 'precipIntensity', 'precipProbability', 'precipType', 'cloudCover', 'humidity', 'summary']
    newSet = []
    for i in range(0,len(dic)):
        newSet.append({})
        for idx in li:
            if (idx in dic[i]):
                newSet[i][idx] = dic[i][idx]
    return newSet

# uses Wikipedia API to get text from the Wiki page on the city
@app.route("/info")
def information():
    if session.get('destination') is None:
        return redirect(url_for('landing_page'))
    data = session['info']
    images = session['images']
    return render_template("information.html", city=session['destination'], info=data, length=len(data),
                           image1=images[0], image2=images[1], image3=images[2])


def img_stuffs(title, page):
    title_encoded = title.replace(' ','%20')
    u = urllib.request.urlopen(
        "https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=images&format=json&imlimit=3".format(
            title_encoded))
    response = u.read()
    img_data = json.loads(response)
    def_image = ['https://scx1.b-cdn.net/csz/news/800/2019/earth.jpg',
                 'https://i.pinimg.com/originals/b0/d5/97/b0d59733d5541b8ecbf628f84fbb863e.png',
                 'https://www.usnews.com/dims4/USNEWS/aa02be1/2147483647/thumbnail/640x420/quality/85/?url=http%3A%2F%2Fcom-usnews-beam-media.s3.amazonaws.com%2Fa3%2Fc9%2F07d54d4543ac9dd2b5c31411b16e%2F2-fairbanks-getty.jpg']
    images = []
    # print(img_data['query']['pages'])
    img_data = img_data['query']['pages'][str(page)]['images']
    for i in img_data:
        url = urllib.request.urlopen(
            "https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=imageinfo&iiprop=url&format=json".format(
                i['title'].replace(' ', '_')))
        response = url.read()
        response_data = json.loads(response)
        try:
            image = response_data['query']['pages']['-1']['imageinfo'][0]['url']
            images.append(image)
        except:
            images = def_image
    print(images)
    return images

# uses the map URL from MapQuest API to get the map
@app.route("/map")
def displayMap():
    if session.get('destination') is None:
        return redirect(url_for('landing_page'))
    zoom = calcZoom(request.args)
    url = getMapUrl(session['desiredLat'],session['desiredLon'],zoom)
    cachemap(url)
    return render_template("map.html", pic = url, newZoom = zoom, city = session['destination'].capitalize())


if __name__ == "__main__":
    app.debug = True
    app.run()
