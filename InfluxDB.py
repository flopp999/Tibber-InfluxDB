# Created by Daniel Nilsson
# Please use my invite-link to help me with my work, we get 500skr each :)
# https://tibber.com/se/invite/8af85f51
# Version 1.0 2020-11-10
# Script to fetch hourly prices from Tibber and write directly to InfluxDB version 1.8

import json,datetime,requests # import libraries

from influxdb import InfluxDBClient, exceptions
# Tibber
token = ""

# InfluxDB variables
database = "Tibber"
measurement = "El"
field = "Pris"

# database information
client = InfluxDBClient('localhost', 8086) # IP, port, user, password

headers = { 'Authorization': 'Bearer '+token, # Tibber Token 'Content-Type': 'application/json',
  'Content-Type': 'application/json'
}

data = '{ "query": "{viewer {homes {currentSubscription {priceInfo {today {total startsAt },tomorrow {total startsAt }}}}}}" }' # asking for today's hourly prices

response = requests.post('https://api.tibber.com/v1-beta/gql', headers=headers, data=data) # make the query to Tibber
response = response._content # selecting the important data from the response
parsed = json.loads(response) # parse it so we can use it easier
jsondata = []
for data in parsed["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["today"]: # go through each hour
  time = data["startsAt"] # store the datetime
  utctime = str(datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").timestamp())[:-2] # change datetime to epoch(seconds) and without decimals
  total = str(round(data["total"]*100,2)) # recalc to kronor instead of öre
  jsondata.append({"measurement": measurement, "time": time, "fields": {field: float(total)}})

for data in parsed["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["tomorrow"]: # go through each hour
  time = data["startsAt"] # store the datetime
  utctime = str(datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").timestamp())[:-2] # change datetime to epoch(seconds) and without decimals
  total = str(round(data["total"]*100,2)) # recalc to kronor instead of öre
  jsondata.append({"measurement": measurement, "time": time, "fields": {field: float(total)}})

try:
  client.write_points(jsondata, database=database, time_precision='n', batch_size=10000, protocol='json') # skriver data till Influx
except exceptions.InfluxDBClientError:	
  print("Couldn\'t save data to InfluxDB database: ")
