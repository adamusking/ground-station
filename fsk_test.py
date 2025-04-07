import time
import threading
import queue
import sys
from LoRaRF import SX127x


radio = SX127x()
radio.setSpi(0, 0)
radio.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

print("Begin FSK radio")
if not radio.writeRegister(0x01, 0b00000000):        # RegOpMode: Sleep, FSK
    raise Exception("Something wrong, can't begin FSK radio")

# ==== Frequency: 866 MHz ====
frf = int(866_000_000 / 61.03515625)  # ≈ 14185551 → 0xD8575F
radio.writeRegister(0x06, (frf >> 16) & 0xFF)  # RegFrfMsb = 0xD8
radio.writeRegister(0x07, (frf >> 8) & 0xFF)   # RegFrfMid = 0x57
radio.writeRegister(0x08, frf & 0xFF)          # RegFrfLsb = 0x5F

# ==== Bitrate: 250 kbps ====
bitrate = int(32_000_000 / 250_000)  # = 128 → 0x0080
radio.writeRegister(0x02, 0x00)  # RegBitrateMsb
radio.writeRegister(0x03, 0x80)  # RegBitrateLsb

# ==== Frequency Deviation: 100 kHz ====
fdev = int(100_000 / 61.03515625)  # ≈ 1639 → 0x0667
radio.writeRegister(0x04, 0x06)  # RegFdevMsb
radio.writeRegister(0x05, 0x67)  # RegFdevLsb

# ==== Rx Bandwidth: 200 kHz ====
# Mantissa=1, Exponent=6 → 0b00011000 = 0x18
radio.writeRegister(0x12, 0x18)  # RegRxBw

# ==== Preamble Length: 5 bytes ====
radio.writeRegister(0x25, 0x00)  # RegPreambleMsb
radio.writeRegister(0x26, 0x05)  # RegPreambleLsb

# ==== CRC ON, Whitening OFF, Variable Packet Length ====
# RegPacketConfig1: bits:
# - bit 7: PacketFormat (0 = variable)
# - bit 4: DCFree (00 = none, 01 = whitening)
# - bit 2: CRC (1 = on)
# → 0b00000100 = 0x04
radio.writeRegister(0x30, 0x04)  # RegPacketConfig1

# Max power
radio.writeRegister(0x09, 0b10001111)  # RegPaConfig

print("FSK Ground Station Started...")

while True:
    # Request for receiving new FSK packet
    radio.request()
    # Wait for incoming radio packet
    radio.wait()

    print("\n\n---Receiving---")
    # Put received packet to message and counter variable
    message = ""
    while radio.available() > 1:
        message += chr(radio.read())
    counter = radio.read()

    # Print received message and counter
    print(f"{message}  {counter}")

    # Print packet/signal status including RSSI, SNR, and signalRSSI
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(radio.packetRssi(), radio.snr()))
    
    packet_id = int(message.split(',')[0].split(':')[1])
    


    # Show received status in case CRC or header error occur
    status = radio.status()
    if status == radio.STATUS_CRC_ERR:
        print("CRC error")
    elif status == radio.STATUS_HEADER_ERR:
        print("Packet header error")

    ack = f"ACK{packet_id}"
    ack_list = [ord(c) for c in ack]
    counter1 = 0
    
    print("\n\n---Transmitting---")
    radio.beginPacket()
    radio.write(ack_list, len(ack_list))
    radio.write([counter1], 1)
    radio.endPacket()
    
    print(f"Sending: {ack}  {counter1}")
    
    radio.wait()
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(radio.transmitTime(), radio.dataRate()))
    
   
    counter1 = (counter1 + 1) % 256