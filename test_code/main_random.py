import influxdb_client, time, random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "onC-rXnz0Y_RlNFZzTyvfgHYFMBLm_XcCE_YqpTuTbygTqGIYn-4AL9PSn7eOj0b-iqgMb2IcpiOsHn7jAMUJQ=="
org = "ASA"
url = "http://127.0.0.1:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "cansat_telemetry"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

while True:
    

    temperature = round(random.uniform(-15, 30), 2)
    pressure = round(random.uniform(950, 1050), 2)
    CO2 = round(random.uniform(400, 1500), 2)
    CO = round(random.uniform(0, 30), 2)
    CH4 = round(random.uniform(1.8, 3.5), 2)
    NO2 = round(random.uniform(0.2, 1.5), 2)
    SO2 = round(random.uniform(0, 20), 2)
    TVOC = round(random.uniform(0, 1000), 2)
    verticalSpeed = round(random.uniform(8, 11), 2)
    horizontalSpeed = round(random.uniform(8, 11), 2)
    latitude = 48.6685
    longitude = 19.6995
    battery_voltage = round(random.uniform(8, 11), 2)
    battery = round(random.uniform(0, 100), 2)

    # Altitudes (simulated separately)
    gpsAltitude = round(random.uniform(0, 1000), 2)
    pressureAltitude = round(random.uniform(0, 1000), 2)
    gpsAltSeaLevel = round(gpsAltitude + random.uniform(-10, 10), 2)
    pressureAltSeaLevel = round(pressureAltitude + random.uniform(-10, 10), 2)


    # Predicted positions (just slight offset from real positions)
    predictedLatitude = 68.6685
    predictedLongitude = 18.6695

    point = (
        Point("cansat_data")
        .tag("device_id", "cansat_01")
        .field("temperature", temperature / 10)
        .field("pressure", ((pressure * 100) + 80000) / 100)
        .field("batteryVoltage", (battery_voltage / 100) )
        .field("gpsAltitude", gpsAltitude / 10)
        .field("pressureAltitude", pressureAltitude / 10)
        .field("gpsAltSeaLevel", gpsAltSeaLevel / 10)
        .field("pressureAltSeaLevel", pressureAltSeaLevel / 10)
        .field("verticalSpeed", verticalSpeed / 10)
        .field("horizontalSpeed", horizontalSpeed / 10)
        .field("Battery", battery)
        .field("latitude", latitude / 1000000)
        .field("longitude", longitude / 1000000)
        .field("predictedLongitude", predictedLongitude / 1000000)
        .field("predictedLatitude", predictedLatitude / 1000000)
        .field("CO2", CO2 / 10)
        .field("CO", CO / 100)
        .field("CH4", CH4 / 100)
        .field("NO2", NO2 / 100)
        .field("SO2", SO2 / 100)
        .field("TVOC", TVOC)
    )

    print("\n\n")
    print("---WRITTING TO INFLUXDB---")
    print(
    f'Written point: Temperature: {temperature}, Pressure: {((pressure * 100) + 80000) / 100}, '
    f'GPS Altitude: {gpsAltitude}, Pressure Altitude: {pressureAltitude}, '
    f'GPS Altitude (Sea Level): {gpsAltSeaLevel}, Pressure Altitude (Sea Level): {pressureAltSeaLevel}, '
    f'Horizontal Speed: {horizontalSpeed}, Vertical Speed: {verticalSpeed}, Battery: {battery}, Latitude: {latitude}, Longitude: {longitude}, '
    f'Predicted Latitude: {predictedLatitude}, Predicted Longitude: {predictedLongitude}, '
    f'CO₂: {CO2}, CO: {CO}, CH₄: {CH4}, NO₂: {NO2}, SO₂: {SO2}, TVOC: {TVOC}'
    )
    write_api.write(bucket=bucket, org=org, record=point)
    time.sleep(1)
