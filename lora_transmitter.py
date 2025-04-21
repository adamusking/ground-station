import time
from LoRaRF import SX127x

# Initialize LoRa module
lora = SX127x()

# Set SPI bus configuration (SPI bus 0, chip select 0)
lora.setSpi(0, 0)

# Set GPIO pins: NSS (CS), RESET, and DIO0 (IRQ)
lora.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

# Begin LoRa module
if not lora.begin():
    raise Exception("Something is wrong, can't initialize LoRa radio")

# Set frequency to 915 MHz
print("Set frequency to 915 MHz")
lora.setFrequency(866000000)

# Set TX power to +17 dBm using PA_BOOST
print("Set TX power to +17 dBm")
lora.setTxPower(17, lora.TX_POWER_PA_BOOST)

# Configure modulation parameters
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
lora.setSpreadingFactor(7)
lora.setBandwidth(125000)
lora.setCodeRate(5)

# Configure packet parameters
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
lora.setHeaderType(lora.HEADER_EXPLICIT)
lora.setPreambleLength(8)
#lora.setPayloadLength(15)
lora.setCrcEnable(True)

# Set synchronization word
print("Set synchronization word to 0x34")
lora.setSyncWord(0xA5)

print("\n-- LoRa Transmitter --\n")

# Message to transmit
message = "HeLoRa World!\0"
message_list = [ord(c) for c in message]
counter = 0

# Transmit message continuously
while True:
    lora.beginPacket()
    lora.write(message_list, len(message_list))
    lora.write([counter], 1)
    lora.endPacket()
    
    print(f"{message}  {counter}")
    
    lora.wait()
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(lora.transmitTime(), lora.dataRate()))
    
    time.sleep(5)
    counter = (counter + 1) % 256
