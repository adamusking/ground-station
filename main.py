import influxdb_client, time, random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from lora_influx import receive_packets, lora

token = "pceFzsaIvLUuLJI-S86z1PjsbryT5gqnhBEWGRfrhH39pwN7G6SAU5ZWEgY_YAYyuiqp6HhFcGq4p2WhqGo5dg=="
org = "ASA"
url = "http://127.0.0.1:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)
bucket = "cansat_telemetry"
write_api = write_client.write_api(write_options=SYNCHRONOUS)

counter1 = 0

while True:
    print("\n\n")
    print("---RECEIVING---")
    message, packet_id = receive_packets()
    print("Received message:", message)

    ack = f"ACK{packet_id}"
    ack_list = [ord(c) for c in ack]

    print("\n\n")
    print("---TRANSMITTING ACK---")
    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    lora.write([counter1], 1)
    lora.endPacket()
    lora.wait()

    print(f"Sent ACK: {ack}  {counter1}")
    print("Transmit time: {0:.2f} ms | Data rate: {1:.2f} byte/s".format(
        lora.transmitTime(), lora.dataRate()))

    counter1 = (counter1 + 1) % 256
  
    temperature = float(message.split(",")[1])
    pressure = float(message.split(",")[2])
    CO2 = float(message.split(",")[3])
    CO = float(message.split(",")[4])
    CH4 = float(message.split(",")[5])     
    N2O = float(message.split(",")[6])
    S2O = float(message.split(",")[7])
    speed = float(message.split(",")[8])
    latitude = float(message.split(",")[9])
    longitude = float(message.split(",")[10])
    battery = float(message.split(",")[11])
    altitude = float(message.split(",")[12])
    
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

    

    time.sleep(1)
