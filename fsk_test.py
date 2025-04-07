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
    packet_id = "UNKNOWN"  # Default in case no ID is found
    command = ""
    
    radio.request()
    radio.wait()

    message = ""
    while radio.available() > 1:
        message += chr(radio.read())
    counter = radio.read()

    print(f"{message}  {counter}")
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(radio.packetRssi(), radio.snr()))
    
    status = radio.status()
    if status == radio.STATUS_CRC_ERR:
        print("CRC error")
    elif status == radio.STATUS_HEADER_ERR:
        print("Packet header error")

    if message.startswith("ID"):
        parts = message.split(",")  # Split by comma
        if len(parts) > 0:
            packet_id = parts[0].split(":")[1]  # Extract ID value
    

    time.sleep(0.1)

    ack = f"ACK{packet_id}, {command}"
    ack_list = [ord(c) for c in ack]
    counter1 = 0

    radio.beginPacket()
    radio.write(ack_list, len(ack_list))
    radio.write([counter], 1)
    radio.endPacket()
    
    print(f"Packet sent: {ack}  {counter}") 
    
    radio.wait()
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(radio.transmitTime(), radio.dataRate()))
    
    counter = (counter + 1) % 256

    '''
    if mode != prev_mode:
        if mode:
            print(f"Switching to LoRa...")
            radio.set_mode_rx()  # LoRa mode (default)
        else:
            print(f"Switching to FSK...")
            radio.write_register(0x2C, 0x10)  # Enable CRC for FSK
            radio.write_register(0x01, 0x00)  # Put radio in standby
            radio.write_register(0x01, 0x20)  # Set to FSK mode
            radio.set_mode_rx()  # Back to RX
        
        prev_mode = mode  # Update the last mode
    '''