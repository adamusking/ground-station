<p align="center">
  <img width="3595" height="2084" alt="image" src="https://github.com/user-attachments/assets/972b4348-90fc-4816-bf2c-7195b86cb4eb" />
</p>

# CanSat_01 Ground Station

The **Ground Station** is the central hub for receiving, storing, and visualizing data from the CanSat_01 mission. It is built using a **Raspberry Pi 4** and leverages several technologies for real-time monitoring and data management.

---

## Overview

The Ground Station performs the following tasks:

- **Telemetry Reception** – Receives sensor data from the CanSat via **LoRa**.  
- **Data Storage** – Stores telemetry data locally in **CSV files** and in **InfluxDB 2** for time-series management.  
- **Data Visualization** – Displays real-time telemetry and historical data using **Grafana** dashboards.  
- **File Transfer** – Receives images and CSV files from the CanSat SD card via **WiFi** and stores them on an **FTP server**.

---

## WiFi-Based File Transfer Protocol

The CanSat can connect to the Ground Station over WiFi using a USB WiFi dongle connected to the Raspberry Pi. The communication flow is as follows:

1. **Command Acknowledgment** – After receiving telemetry, the Ground Station can send an **ACK** with a command:
   - `WIFI` → instructs the CanSat to connect to the Ground Station’s WiFi and transfer images/CSV files to the FTP server.  
   - `WIFI_NO` → instructs the CanSat to disconnect from WiFi to save power.  

2. **File Transfer** – When the `WIFI` command is received, the CanSat uploads the data from its SD card to the FTP server running on the Ground Station.  

3. **Power Efficiency** – The `WIFI_NO` command ensures the CanSat disconnects from WiFi when not needed, conserving battery power during the mission.

---

## Repository Structure

- **`main.py`** – Main Ground Station script handling LoRa reception, ACK commands, and data routing.  
- **`lora.py`** – LoRa communication interface.  
- **`csv_logger.py`** – Handles local CSV logging.  
- **`influxdb_handler.py`** – Stores and retrieves telemetry data from InfluxDB 2.  
- **`ftp_server/`** – FTP server configuration for image and CSV file reception.  
- **`grafana/`** – Grafana dashboards for real-time visualization.
<p align="center>
  <img width="2838" height="1220" alt="image" src="https://github.com/user-attachments/assets/b70e2b0b-1930-415f-a03d-e745c55c0aad"/>
  <img width="1420" height="686" alt="image" src="https://github.com/user-attachments/assets/0712c4d8-d04c-41d6-8476-5608bb670d1d" />
</p>

---

## Requirements

- **Hardware:** Raspberry Pi 4, LoRa module, USB WiFi dongle.  
- **Software:** Python 3.x, InfluxDB 2, Grafana, FTP server software.  

---

