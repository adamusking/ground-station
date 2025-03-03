from time import sleep
from radiolib import SX1276

radio = SX1276(868.0, 500.0, 7, 5, 0x3F, 17, 8, 0)
commands = ""

print("LoRa Ground Station Started...")

while True:
    packet = radio.receive(timeout = 1000)
    if packet:
            print(f"Received: {packet}")

            if packet.startswith("ID:"):
                packet_id = packet.split(",")[0].split(":")[1]

                
                ack = f"ACK{packet_id} + ,{commands}"
                print(f"Sending ACK: {ack}")
                radio.transmit(ack)