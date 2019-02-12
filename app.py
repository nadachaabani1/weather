#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

import requests
import json
from requests_oauthlib import OAuth1,OAuth1Session

from datetime import datetime

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

   
    return  processRequest(req)


def processRequest(req):
    print ("started processing")
    result = req.get("result")
    if result.get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://weather-ydn-yql.media.yahoo.com/forecastrss?location="
    
    usr = baseurl + result.get("parameters").get("geo-city")+"&format=json"
    result = requests.post(url=usr,auth=OAuth1("dj0yJmk9M0NIMnNnelZoSXhWJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWE1",client_secret="63d15162cb96eeeea9eddeac95c36283005a252e"))

    print("yql result: ")

    response= json.loads(result.text)
    print(response.get("location"))

    
    
    
    return json.dumps(makeWebhookResult(response))


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):

    location = data.get('location')
    print(location)
    current_observation=data.get('current_observation')
    print(current_observation)
    print(current_observation.get('pubDate'))
    print(type(current_observation.get('pubDate')))

    ts = current_observation.get('pubDate')
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print(date)
    print(type(str(current_observation.get('pubDate'))))
    condition = current_observation.get('condition')
    
    print(condition)
    fahrenheit = condition.get('temperature')
    celsius = int((fahrenheit - 32) / 1.8)

    print(str(condition.get('temperature')))
    print(type(condition.get('temperature')))
    print(type(str(condition.get('temperature'))))

    
    if (location is None) or (condition is None):
        return {}


    # print(json.dumps(item, indent=4))
    
    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
            ", the temperature at " + date + " is " + str(celsius) + "°C."
    ss = {"fulfillment": {
                "speech": speech
            }
    }
    
    print("Response:")
    print(speech)

    

    


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
