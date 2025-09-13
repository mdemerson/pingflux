# Pingflux
Pingflux is a Python tool for monitoring network latency. It pings a list of URLs or IPs, collects response times, and stores the results in an InfluxDB v1.x database. With the data in Influx, you can easily build dashboards (e.g., with Grafana) to visualize latency trends and detect connectivity issues.

Features
	•	Continuous ping monitoring of URLs or IP addresses
	•	Records timestamp and latency for each probe
	•	Stores results in InfluxDB v1.x
	•	Simple JSON structure for intermediate data handling
	•	Easy integration with visualization tools like Grafana

Use Cases
	•	Track latency to critical hosts or services
	•	Monitor uptime and performance of network infrastructure
	•	Build dashboards to spot spikes, downtime, or degraded performance
