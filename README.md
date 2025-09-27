<p align="center">
  <img width="3595" height="2084" alt="image" src="https://github.com/user-attachments/assets/972b4348-90fc-4816-bf2c-7195b86cb4eb"/>
</p>

# CanSat_01 Ground Station

The **Ground Station** is the central hub for receiving, storing, and visualizing data from the CanSat_01 mission. It is built using a **Raspberry Pi 4** and leverages several technologies for real-time monitoring and data management.

---


## Repository Structure

- **`main.py`** – Main Ground Station script handling LoRa reception, ACK commands, CSV logging, and data routing.  
- **`lora.py`** – LoRa communication interface for receiving telemetry from the CanSat.  
- **`img_processing.py`** – Processes images from the CanSat to analyze **light pollution**.  
- **`data.csv`** – Local CSV log of received telemetry data.  
- **`test_code/`** – Scripts for testing and validating individual components of the ground station.  
- **`__pycache__/`** – Python cache files (automatically generated).  

---

## Overview

The Ground Station performs the following tasks:

- **Telemetry Reception** – Receives sensor data from the CanSat via **LoRa**.  
- **Data Storage** – Stores telemetry data locally in **CSV files** and in **InfluxDB 2** for time-series management.  
- **Data Visualization** – Displays real-time telemetry and historical data using **Grafana** dashboards.  
- **File Transfer** – Receives images and CSV files from the CanSat SD card via **WiFi** and stores them on an **FTP server**.

---

## LoRa Telemetry Reception

The Ground Station uses a **LoRa module** connected to the Raspberry Pi 4 to receive telemetry data from the CanSat.  

- **Data received:** Altitude, temperature, pressure, CO₂, SO₂, and other sensors.  
- **Command transmission:** The Ground Station sends ACK commands (`WIFI` / `WIFI_NO`) back to the CanSat via LoRa.  
- **Low-power, long-range communication:** LoRa enables reliable telemetry reception over the full mission range (~1 km altitude).


## WiFi-Based File Transfer Protocol

The CanSat can connect to the Ground Station over WiFi using a USB WiFi dongle connected to the Raspberry Pi. The communication flow is as follows:

1. **Command Acknowledgment** – After receiving telemetry, the Ground Station can send an **ACK** with a command:
   - `WIFI` → instructs the CanSat to connect to the Ground Station’s WiFi and transfer images/CSV files to the FTP server.  
   - `WIFI_NO` → instructs the CanSat to disconnect from WiFi to save power.  

2. **File Transfer** – When the `WIFI` command is received, the CanSat uploads the data from its SD card to the FTP server running on the Ground Station.  

3. **Power Efficiency** – The `WIFI_NO` command ensures the CanSat disconnects from WiFi when not needed, conserving battery power during the mission.

---

## Data Visualization

The Ground Station visualizes telemetry data using **Grafana dashboards**, showing both real-time and historical measurements.

<p align="center">
  <img width="800" height="1000" alt="image" src="https://github.com/user-attachments/assets/b70e2b0b-1930-415f-a03d-e745c55c0aad"/>
</p>
<p align="center">
  <img width="800" height="1000" alt="image" src="https://github.com/user-attachments/assets/0712c4d8-d04c-41d6-8476-5608bb670d1d"/>
</p>

The dashboards include:

- Real-time sensor readings (temperature, pressure, CO₂, SO₂, etc.)
- Historical trends stored in **InfluxDB 2**

---

## Light Pollution Analysis

In addition to standard telemetry, the Ground Station processes images from the CanSat to analyze **light pollution**. This is handled by the `img_processing.py` script and involves:

- Receiving images from the CanSat SD card via WiFi/FTP.
- Analyzing brightness and light intensity to estimate light pollution in the surveyed area.
- Storing results locally or in CSV for further analysis.
  
<div style="display: flex; justify-content: center; align-items: center;">
  <img src="https://github.com/user-attachments/assets/d018b6a4-0ddf-49dc-a820-7c0ca4a77e7a" alt="Image 1" width="300"/>
  <img src="https://github.com/user-attachments/assets/9d4708b8-715a-43c8-9361-770bc6c737be" alt="Image 2" width="300"/>
</div>

---

## Requirements

- **Hardware:** Raspberry Pi 4, LoRa module, USB WiFi dongle.  
- **Software:** Python 3.x, InfluxDB 2, Grafana, FTP server software.  

---

