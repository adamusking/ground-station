import influxdb_client, time, random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "I3UpUY4J4S1oYxYpry8KZ-JS4wInVChIouw_n5URylAuFnALEikjkI18H8X3Cms7unIKOmgLhlSknxABeNC52A=="
org = "ASA"
url = "http://172.16.0.50:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "test_data"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:
    temperature = round(random.uniform(-10, 30), 2)
    humidity = round(random.uniform(0, 100), 2)
    pressure = round(random.uniform(950, 1050), 2)
    CO2 = round(random.uniform(400, 600), 2)
    CO = round(random.uniform(0, 9), 2)
    CH4 = round(random.uniform(1, 3), 2)
    N2O = round(random.uniform(300, 350), 2)
    S2O = round(random.uniform(0, 50), 2)
    latitude = round(random.uniform(-90, 90), 6)
    longitude = round(random.uniform(-180, 180), 6)
    battery = round(random.uniform(3.5, 4.2), 2)
    altitude = round(random.uniform(0, 1000), 2)

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

    print(f'Written point: Temperature: {temperature}, Altitude: {altitude}, Humidity: {humidity}, '
          f'Pressure: {pressure}, CO2: {CO2}, CO: {CO}, CH4: {CH4}, N2O: {N2O}, S2O: {S2O}, '
          f'Latitude: {latitude}, Longitude: {longitude}, Battery: {battery}')
    write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(1)
