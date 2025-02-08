import influxdb_client, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "token"
org = "org_name"
url = "influxdb_url"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="bucket_name"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:

  point = (
    Point("cansat_data")
    .tag("device_id", "cansat_01")
    .field("temperature", temperature)
    .field("humidity", humidity)
    .field("pressure", pressure)
    .field("CO2", CO2)
    .field("CO", CO)
    .field("CH4", CH4)
    .field("N2O", N2O)
    .field("S2O", S2O)
    .field("latitude", latitude)
    .field("longitude", longitude)
    .field("Battery", battery)
    .field("altitude", altitude)
  )

  print(f'Written point: Temperature: {temperature}, Altitude: {altitude},  Humidity: {humidity}, Pressure: {pressure}, CO2: {CO2},CO: {CO}, CH4: {CH4}, N2O: {N2O}, S2O: {S2O}, Latitude: {latitude}, Longitude: {longitude}, Battery: {battery}')
  write_api.write(bucket=bucket, org="org_name", record=point)
  time.sleep(1)
