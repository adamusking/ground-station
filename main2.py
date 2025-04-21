import influxdb_client, time, random, csv, os
from datetime import datetime 
import RPi.GPIO as GPIO
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from lora_influx2 import receive_packets, lora

pinLED1 = 6 # received  
pinLED2 = 13  # transmitted

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pinLED1, GPIO.OUT)
GPIO.setup(pinLED2, GPIO.OUT)

token = "pceFzsaIvLUuLJI-S86z1PjsbryT5gqnhBEWGRfrhH39pwN7G6SAU5ZWEgY_YAYyuiqp6HhFcGq4p2WhqGo5dg=="
org = "ASA"
url = "http://127.0.0.1:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "cansat_telemetry"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

#counter1 = 0

header_names = ["time", "temperature", "pressure", "CO2", "CO", "CH4", "N2O", "S2O", "speed", "latitude", "longitude", "battery", "altitude"]

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
    print("\n\n")
    print("---RECEIVING---")
    raw_data = receive_packets()
    
    now = datetime.now()

    receive_time = now.isoformat() 

    blink_led(pinLED1)

    packet_id = raw_data[0]
    ack = f"ACK{packet_id}"
    ack_list = [ord(c) for c in ack]

    print("\n\n")
    print("---TRANSMITTING ACK---")
    time.sleep(0.2)
    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    #lora.write([counter1], 1)
    lora.endPacket()
    lora.wait()
    
    blink_led(pinLED2)

    print(f"Sent ACK: {ack}")
    print("Transmit time: {0:.2f} ms | Data rate: {1:.2f} byte/s".format(
        lora.transmitTime(), lora.dataRate()))

    #counter1 = (counter1 + 1) % 256
    
    temperature = float(raw_data[1])
    pressure = float(raw_data[2])
    CO2 = float(raw_data[3])
    CO = float(raw_data[4])
    CH4 = float(raw_data[5])
    N2O = float(raw_data[6])
    S2O = float(raw_data[7])
    speed = float(raw_data[8])
    latitude = float(raw_data[9])
    longitude = float(raw_data[10])
    battery = float(raw_data[11])
    altitude = float(raw_data[12])

    
    point = (
        Point("cansat_data")
        .tag("device_id", "cansat_01")
        .field("temperature", temperature)
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

    print("\n\n")
    print("---WRITTING TO INFLUXDB---")
    print(f'Written point: Temperature: {temperature}, Altitude: {altitude}, '
          f'Pressure: {pressure}, CO2: {CO2}, CO: {CO}, CH4: {CH4}, N2O: {N2O}, S2O: {S2O}, '
          f'Latitude: {latitude}, Longitude: {longitude}, Battery: {battery}, Speed: {speed}')
    write_api.write(bucket=bucket, org=org, record=point)
        
     
    data_row = [
            receive_time, raw_data[1], raw_data[2], raw_data[3], raw_data[4], raw_data[5], raw_data[6],
            raw_data[7], raw_data[8], raw_data[9], raw_data[10], raw_data[11], raw_data[12]
        ]

    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_row)
    
    

    time.sleep(1)
