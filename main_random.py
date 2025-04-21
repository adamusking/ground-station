import influxdb_client, time, random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "pceFzsaIvLUuLJI-S86z1PjsbryT5gqnhBEWGRfrhH39pwN7G6SAU5ZWEgY_YAYyuiqp6HhFcGq4p2WhqGo5dg=="
org = "ASA"
url = "http://127.0.0.1:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "cansat_telemetry"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:
    temperature = round(random.uniform(-15, 30), 2)
    humidity = round(random.uniform(0, 100), 2)
    pressure = round(random.uniform(950, 1050), 2)
    CO2 = round(random.uniform(400, 1500), 2)
    CO = round(random.uniform(0, 30), 2)
    CH4 = round(random.uniform(1.8, 3.5), 2)
    N2O = round(random.uniform(0.2, 1.5), 2)
    S2O = round(random.uniform(0, 20), 2)
    speed = round(random.uniform(8, 11), 2)
    latitude = 48.6690
    longitude = 19.6990
    battery = round(random.uniform(0, 100), 2)
    altitude = round(random.uniform(0, 1000), 2)

    point = (
        Point("cansat_data")
        .tag("device_id", "cansat_01")
        .field("temperature", temperature)
        .field("humidity", humidity)
        .field("pressure", pressure)
        .field("CO2", CO2)
        .field("CO", CO)
        .field("speed", speed)
        .field("CH4", CH4)
        .field("N2O", N2O)
        .field("S2O", S2O)
        .field("latitude", latitude)
        .field("longitude", longitude)
        .field("Battery", battery)
        .field("altitude", altitude)
    )

    print(f'Written point: Temperature: {temperature}, Altitude: {altitude}, Humidity: {humidity}, '
          f'Pressure: {pressure}, CO2: {CO2}, CO: {CO}, CH4: {CH4}, N2O: {N2O}, S2O: {S2O}, '
          f'Latitude: {latitude}, Longitude: {longitude}, Battery: {battery}, Speed: {speed}')
    write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(1)
