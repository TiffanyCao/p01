# Ocean Getaways by Team Boneless Ice
## Ayham Alnasser, Clement Chan, Kiran Vuksanaj, and Tiffany Cao (PM)

#### PROGRAM OVERVIEW:

This website is essentially a helping guide to travelers going to other cities or countries globally. There is a single search form, allowing the users to input a city and country, which will be stored in a session. If the given city and country doesn’t exist, the website will throw an error message. Using the IPStack API, we can obtain the user’s location, which we can then use to compute the currency exchange, using the Currency Exchange API. The website will also show information regarding the weather conditions of the city given using the Dark Sky API. Finally, using MapQuest and Wikipedia Images, users will be provided with images and a map of the city they gave. As an extra feature, there will also be a small section from the Wikipedia API about the city or country given.


#### INSTRUCTIONS FOR INSTALLATION

Before beginning, ensure that you have access to git commands and python3 on your terminal. If you have only python3 and not python2 installed, all instances of pip3 and python3 may be replaces with pip and python.

In order to download the source code for the app, call
```bash
git clone https://github.com/TiffanyCao/p01.git
```

Navigate into this directory, and install the necessary python library requirements with
```bash
pip3 install -r requirements.txt
```

If you do not have access to the pip3 command, you can instead create a virtual environment with
```bash
python3 -m venv <virtual_environment_name>
. <virtual_environment_name>/bin/activate
```
and then resume installing normally.

*Procure keys for the Mapquest developer API and the Dark Sky Weather API before proceeding. When you have successfully procured keys, replace the dummy text in keys.json with your request keys.*
**See below for instructions on key installation!**

The app can be launched when keys have successfully been procured with:
```bash
python3 app.py
```

#### OBTAINING KEYS

None of the below keys require payment information for the beginning of usage. The only necessary resource is an email address.

##### MapQuest Developer API - Geolocation
Documentation [here](https://docs.google.com/document/d/1HnzToCm_MkkXAyboatQQb0dZiSAYDD04QcwS2UFF4XI/edit?usp=sharing)

1. Register for an account on [MapQuest Developer](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register)
  - While you do have to fill out all fields, none matter other than your email address.
2. The landing page post-signup will contain an app titled 'My Application' already created; open the card for the app, and copy the *consumer key*
3. Open the `keys.json` file in your repository, and paste the key in place of `YOUR_API_KEY_HERE` in the 'mapquest' field

##### Dark Sky API - Weather Forecast
Documentation [here](https://docs.google.com/document/d/11P20BGIGfKRNu8uG3Yxn1DkM_quHjr5254bGpjHaX14/edit?usp=sharing)

1. Register an account on [Dark Sky API](https://darksky.net/dev/register)
  - the only required fields are an email and password
2. Confirm your email address by clicking the link sent to the email address entered, and then log in with your new credentials
3. Copy the secret key displayed on the landing page post-login, and paste it into `keys.json` in place of `YOUR_API_KEY_HERE` the 'darksky' field

#### IP Stack API - Geolocation part 2
Documentation [here](https://docs.google.com/document/d/1JLCpSsibgXBVDN8C8FwyYYiO1jIob_qk1owP3F1gNyQ/edit?usp=sharing) 

1. Register an account on [their site](https://ipstack.com/)
2. Open dashboard and yoink the API key you're given
3. Drop the API key into the 'keys.json' in place of the 'YOUR_API...' in the 'ipstack' field

#### OTHER APIs USED - NO KEYS REQUIRED
1. Wikipedia API: This API is used to obtain information on the city, as well as display images of the city in the information page. The Wikipedia API is very expansive and has many different query calls; here are the main calls we used in Ocean Getaways.
  - For obtaining text information: action = query, list = search, srsearch = {city name}, prop = extracts, explaintext, exintro, titles = {title of Wikipedia page}
  - For obtaining urls of images: action = query, titles = {image title}, prop = images, prop = imageinfo, iiprop = url
  - Documentation [here](https://docs.google.com/document/d/1KNf_h_Rysiftc88uZNZO4LMpAyQprUTSj-eg5CMz9a8/edit?usp=sharing)

2. Currency Exchange API: This API is used to obtain currency exchange rates between a given base country and 70 other currencies in the world. 
  - Documentation [here](https://docs.google.com/document/d/1yTckLoGBHA-C37hhukXOc76Jh_770L7m3Moj-wMFeUU/edit?usp=sharing)

3. REST Countries API: This API is used to obtain the local currency of a given country. Used in conjunction with IP Stack to find the country the user's IP address resides in and the currency of that country.
  - Documentation [here](https://docs.google.com/document/d/1C-umxnBAIUzQI9kLDaXG4-YbFsiOwwRTJ5c-DXAHTRM/edit?usp=sharing)

