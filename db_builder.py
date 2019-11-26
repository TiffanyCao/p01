#Team Bonesless Ice
#SoftDev1 Pd 1

import sqlite3   #enable control of an sqlite database
import csv

DB_FILE= "data/travel.db"

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops

#================================================

# "currency" table
command = "CREATE TABLE IF NOT EXISTS currency (base TEXT, destination TEXT, rate REAL, timestamp BLOB)"
c.execute(command)

# place information table
command = "CREATE TABLE IF NOT EXISTS place_info (countrycode TEXT, city TEXT PRIMARY KEY, currency TEXT, latitude REAL, longitude REAL, info TEXT, images TEXT, last_cached TIMESTAMP)"
c.execute(command)

#================================================
db.commit()
db.close()
