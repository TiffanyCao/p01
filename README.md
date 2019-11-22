# Ocean Getaways by Team Boneless Ice
## Ayham Alnasser, Clement Chan, Kiran Vuksanaj, and Tiffany Cao (PM)

#### PROGRAM OVERVIEW:

This website is essentially a helping guide to travelers going to other cities or countries globally. There is a single search form, allowing the users to input a city and country, which will be stored in a session. If the given city and country doesn’t exist, the website will throw an error message. Using the IP Location API, we can obtain the user’s location, which we can then use to compute the currency exchange, using the Currency Exchange API. The website will also show information regarding the weather and air quality of the city given using the Dark Sky and Air Visual APIs, respectively. Finally, using NASA and On Splash, users will be provided with images and a map of the city and/or country they gave. As an extra feature, there will also be a small section from the Wikipedia API about the city or country given.


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

The app can be launched when keys have successfully been procured with:
```bash
python3 app.py
```