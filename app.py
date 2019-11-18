# Team Boneless Ice - Ayham Alnasser, Tiffany Cao, Clement Chan, Kiran Vuksanaj
# SoftDev1 pd1
# P01 -- flask app, ocean getaways
# 2019-11-18

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def landing_page():
    return render_template("welcome.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
