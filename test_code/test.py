import influxdb_client, time, random, csv, os
import threading
import queue
import sys
from datetime import datetime 
import RPi.GPIO as GPIO
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from lora_test import receive_packets, lora
from dataclasses import dataclass
import struct

# --- GPIO Setup ---
pinLED1 = 6 # received  
pinLED2 = 13  # transmitted

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinLED1, GPIO.OUT)
GPIO.setup(pinLED2, GPIO.OUT)

# --- InfluxDB Setup ---
token = "pceFzsaIvLUuLJI-S86z1PjsbryT5gqnhBEWGRfrhH39pwN7G6SAU5ZWEgY_YAYyuiqp6HhFcGq4p2WhqGo5dg=="
org = "ASA"
url = "http://127.0.0.1:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "cansat_test"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

# --- CSV Setup ---
header_names = ["time", "temperature", "pressure", "gpsAltitude", "pressureAltitude", "gpsAltSeaLevel", "pressureAltSeaLevel", "verticalSpeed","horizontalSpeed", "battery", "latitude", "longitude", "predictedLongitude", "predictedLatitude",  "CO2", "CO", "CH4", "NO2", "SO2", "TVOC"]
if not os.path.isfile('data.csv'):
    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_names)

# --- Threaded Input Handling ---
input_queue = queue.Queue()
def read_input():
    """Reads full-line input in a separate thread and stores it in a queue."""
    while True:
        user_input = sys.stdin.readline().strip()
        input_queue.put(user_input)

threading.Thread(target=read_input, daemon=True).start()
print("Type a command and press Enter.")

# --- Helper Functions ---
def blink_led(pin, duration=0.1):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

# --- Main Loop ---
while True:
    # --- Handle Console Commands ---
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

    telemetry_format = '<H H H H H H H H H H L L L L H H H H H H'
    telemetry_size = struct.calcsize(telemetry_format)
    unpacked = list(struct.unpack(telemetry_format, byte_array[:telemetry_size]))
    unpacked = list(map(float, unpacked))

    print(unpacked)

    (packetID, temperature, pressure, gpsAltitude, pressureAltitude, gpsAltSeaLevel,
     pressureAltSeaLevel, verticalSpeed, horizontalSpeed, battery, latitude, longitude,
     predictedLongitude, predictedLatitude, CO2, CO, CH4, NO2, SO2, TVOC) = unpacked

    ack = f"ACK{int(packetID)}, {command}"
    ack_list = [ord(c) for c in ack]

    print("\n\n")
    print("---TRANSMITTING ACK---")
    time.sleep(0.75)
    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    lora.endPacket()
    lora.wait()

    blink_led(pinLED2)

    print(f"Sent ACK: {ack}")
    print("Transmit time: {0:.2f} ms | Data rate: {1:.2f} byte/s".format(
        lora.transmitTime(), lora.dataRate()))

    # Write to InfluxDB
    point = (
        Point("cansat_data")
        .tag("device_id", "cansat_01")
        .field("temperature", temperature)
        .field("pressure", pressure)
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
    print("---WRITING TO INFLUXDB---")
    print(
        f'Written point: Temperature: {temperature}, Pressure: {pressure}, '
        f'GPS Altitude: {gpsAltitude}, Pressure Altitude: {pressureAltitude}, '
        f'GPS Altitude (Sea Level): {gpsAltSeaLevel}, Pressure Altitude (Sea Level): {pressureAltSeaLevel}, '
        f'Horizontal Speed: {horizontalSpeed}, Vertical Speed: {verticalSpeed}, Battery: {battery}, Latitude: {latitude}, Longitude: {longitude}, '
        f'Predicted Latitude: {predictedLatitude}, Predicted Longitude: {predictedLongitude}, '
        f'CO₂: {CO2}, CO: {CO}, CH₄: {CH4}, NO₂: {NO2}, SO₂: {SO2}, TVOC: {TVOC}'
    )
    write_api.write(bucket=bucket, org=org, record=point)

    # Write to CSV
    unpacked[0] = receive_time
    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(unpacked)

    time.sleep(1)
