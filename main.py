import influxdb_client, time, random, csv, os
import threading
import queue
import sys
from datetime import datetime 
import RPi.GPIO as GPIO
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from lora import receive_packets, lora
from dataclasses import dataclass
from dotenv import load_dotenv
import struct

pinLED1 = 6 # received  
pinLED2 = 13  # transmitted

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinLED1, GPIO.OUT)
GPIO.setup(pinLED2, GPIO.OUT)

load_dotenv()

token = os.getenv("INFLUX_TOKEN")
org = os.getenv("INFLUX_ORG")
url = os.getenv("INFLUX_URL")
bucket = os.getenv("INFLUX_BUCKET")

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = os.getenv("INFLUX_BUCKET")
write_api = write_client.write_api(write_options=SYNCHRONOUS)

header_names = ["time","temperature","pressure","gpsAltitude","pressureAltitude","gpsAltSeaLevel", "pressureAltSeaLevel","verticalSpeed","horizontalSpeed","batteryVoltage","battery","latitude","longitude", "predictedLongitude","predictedLatitude","CO2","CO","CH4","NO2","SO2","TVOC"]

input_queue = queue.Queue()
def read_input():
    """Reads full-line input in a separate thread and stores it in a queue."""
    while True:
        user_input = sys.stdin.readline().strip()
        input_queue.put(user_input)

threading.Thread(target=read_input, daemon=True).start()
print("Type a command and press Enter.")

file_exists = os.path.isfile('data.csv')

if not file_exists:
    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_names)

def blink_led(pin, duration=0.1):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

while True:
    command = ""
    if not input_queue.empty():
        command = input_queue.get()
        print(f"Received command: {command}")
        # Optional: implement command handling logic here (e.g., terminate, pause, debug, etc.)
        if command.lower() == "exit":
            print("Exiting script.")
            break

    print("\n\n")
    print("---RECEIVING---")
    raw_data = receive_packets()
    byte_array = bytearray(raw_data)
    print(f"Bytearray: {byte_array}")
    now = datetime.now()

    receive_time = now.isoformat() 

    blink_led(pinLED1)

    telemetry_format = '<H H H H H H H H H H L L L L H H H H H H' #H => 10 + 6 = 16 * 2 = 32B | L => 4 * 4 = 16B | 32 + 16 = 48B
    telemetry_size = struct.calcsize(telemetry_format)

    unpacked = list(struct.unpack(telemetry_format, byte_array[:telemetry_size]))
    unpacked = list(map(float, unpacked))
    print(unpacked)

    packetID,temperature,pressure,gpsAltitude,pressureAltitude,gpsAltSeaLevel,pressureAltSeaLevel,verticalSpeed,horizontalSpeed,battery_voltage,latitude,longitude,predictedLongitude,predictedLatitude,CO2,CO,CH4,NO2,SO2,TVOC = unpacked
    
    ack = f"ACK{int(packetID)},{command}"
    ack_list = [ord(c) for c in ack]

    print("\n\n")
    print("---TRANSMITTING ACK---")
    time.sleep(0.2)
    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    lora.endPacket()
    lora.wait()
    
    blink_led(pinLED2)

    print(f"Sent ACK: {ack}")
    print("Transmit time: {0:.2f} ms | Data rate: {1:.2f} byte/s".format(
        lora.transmitTime(), lora.dataRate()))

    temperature = temperature / 10
    pressure = ((pressure * 100) + 80000) / 100
    battery_voltage = battery_voltage / 100
    gpsAltitude = gpsAltitude / 10
    pressureAltitude = pressureAltitude / 10
    gpsAltSeaLevel = gpsAltSeaLevel / 10
    pressureAltSeaLevel = pressureAltSeaLevel / 10
    verticalSpeed = verticalSpeed / 10
    horizontalSpeed = horizontalSpeed / 10
    latitude = latitude / 1000000
    longitude = longitude / 1000000
    predictedLongitude = predictedLongitude / 1000000
    predictedLatitude = predictedLatitude / 1000000
    CO2 = CO2 / 10
    CO = CO / 100
    CH4 = CH4 / 100
    NO2 = NO2 / 100
    SO2 = SO2 / 100

    BMS_CUTOFF_VOLTAGE = 6.3
     
    if battery_voltage <= BMS_CUTOFF_VOLTAGE:
        battery = 0.0
    elif battery_voltage >= 8.1: 
        battery = 100.0
    else:
        battery = (((battery_voltage) - BMS_CUTOFF_VOLTAGE) / (8.2 - BMS_CUTOFF_VOLTAGE)) * 100.0

    point = (
        Point("cansat_data")
        .tag("device_id", "cansat_01")
        .field("temperature", temperature)
        .field("pressure", pressure)
        .field("batteryVoltage", battery_voltage)
        .field("gpsAltitude", gpsAltitude)
        .field("pressureAltitude", pressureAltitude)
        .field("gpsAltSeaLevel", gpsAltSeaLevel)
        .field("pressureAltSeaLevel", pressureAltSeaLevel)
        .field("verticalSpeed", verticalSpeed)
        .field("horizontalSpeed", horizontalSpeed)
        .field("Battery", battery)
        .field("latitude", latitude)
        .field("longitude", longitude)
        .field("predictedLongitude", predictedLongitude)
        .field("predictedLatitude", predictedLatitude)
        .field("CO2", CO2)
        .field("CO", CO)
        .field("CH4", CH4)
        .field("NO2", NO2)
        .field("SO2", SO2)
        .field("TVOC", TVOC)
    )

    print("\n\n")
    print("---WRITTING TO INFLUXDB---")
    print(
    f'Written point: Temperature: {temperature}, Pressure: {pressure}, '
    f'GPS Altitude: {gpsAltitude}, Pressure Altitude: {pressureAltitude}, '
    f'GPS Altitude (Sea Level): {gpsAltSeaLevel}, Pressure Altitude (Sea Level): {pressureAltSeaLevel}, '
    f'Horizontal Speed: {horizontalSpeed}, Vertical Speed: {verticalSpeed}, '
    f'Battery %: {battery:.2f}, Battery Voltage: {battery_voltage}, '
    f'Latitude: {latitude}, Longitude: {longitude}, '
    f'Predicted Latitude: {predictedLatitude}, Predicted Longitude: {predictedLongitude}, '
    f'CO₂: {CO2}, CO: {CO}, CH₄: {CH4}, NO₂: {NO2}, SO₂: {SO2}, TVOC: {TVOC}'
)

    write_api.write(bucket=bucket, org=org, record=point)
        
    data_row = [
    receive_time,temperature,pressure,gpsAltitude,pressureAltitude,gpsAltSeaLevel,pressureAltSeaLevel,verticalSpeed, horizontalSpeed,battery_voltage,battery,latitude,longitude,predictedLongitude,predictedLatitude,CO2,CO,CH4,NO2,SO2,TVOC
    ] 

    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_row)
    
    time.sleep(1)
