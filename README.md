# Pingflux

**Pingflux** is a Python tool for monitoring network latency. It pings a list of URLs or IPs, collects response times, and stores the results in an **InfluxDB v1.x** database. With the data in Influx, you can easily build dashboards (e.g., with **Grafana**) to visualize latency trends and detect connectivity issues.

## Features
- Continuous ping monitoring of URLs or IP addresses
- Records timestamp and latency for each probe
- Stores results in **InfluxDB v1.x**
- Simple JSON structure for intermediate data handling
- Easy integration with visualization tools like **Grafana**

## Use Cases
- Track latency to critical hosts or services
- Monitor uptime and performance of network infrastructure
- Build dashboards to spot spikes, downtime, or degraded performance

---

# Installation on Boot (Ubuntu)

This guide shows how to set up **Pingflux** as a systemd service so it runs automatically on boot.

## 1. Create the service file
Open a new service definition:

```bash
sudo nano /etc/systemd/system/pingflux.service
```

## 2. Add the following configuration

Paste the following into the file (update the paths and username as needed):

```ini
[Unit]
Description=Pingflux Service
After=network.target

[Service]
User=your_username
ExecStart=/path/to/venv/bin/python3 /path/to/pingflux.py
WorkingDirectory=/path/to/pingflux_directory
Restart=always

[Install]
WantedBy=multi-user.target
```

Save and exit (CTRL+O, Enter, CTRL+X).

## 3. Enable and start the service

Reload systemd, enable the service on boot, and start it immediately:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pingflux.service
sudo systemctl start pingflux.service
```
