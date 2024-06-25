from flask import Flask, render_template, url_for
import datetime as dt
import requests

BASE_URL = "http://api.weatherapi.com/v1/current.json?"
API_KEY = "d498671aedb94e0db19135450242506"
CITY = "LONDON" 
# "key= &q=London&aqi=no"

URL = BASE_URL + 'key=' + API_KEY + "&q=" + CITY

respone = requests.get(URL).json()
print(respone)

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)
    