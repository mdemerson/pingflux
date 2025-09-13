#!/usr/bin/env python3
import yaml #pip install pyaml
import subprocess as sp
from influxdb import InfluxDBClient

# Load our config
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        targets = []
        db_host = config['influxdb']['host']
        db_port = config['influxdb']['port']
        db_name = config['influxdb']['dbname']
        db_user = config['influxdb']['dbuser']
        db_pass = config['influxdb']['dbpass']
        for host in config['hosts']:
            targets.append(host['hostaddress'])
except FileNotFoundError:
    print("Error: config.yaml not found.")
except yaml.YAMLError as exc:
    print(f"Error parsing YAML file: {exc}")

def get_fping_results(targets):
    """
    Executes fping and returns its output.
    :param targets: A list of hostnames or IP addresses to ping.
    :return: The raw output of the fping command as a string.
    """
    # Construct the fping command with desired options
    # -q: quiet output, only shows summary
    # -C count: send count pings to each target
    # command = ['fping', '-B 1', '-D', '-r 0', '-O 0', '-Q 10', '-l'] + targets
    command = ['fping', '-D', '-b 56', '-l', '-r 0' '-p 1000'] + targets
    try:
        # Execute the command and capture stdout and stderr
        process = sp.Popen(
            command,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            text=True,  # Decode output as text
            bufsize=1,
            universal_newlines=True # better newline handling
        )
        print(f"running command: {' '.join(command)}")
        print("--- output ---")
        for line in process.stdout:
            parts  = line.strip().split()
            # Check for timeout
            url = parts[1]
            if parts[4] == "timed":
                ping = str("")
            else:
                ping = parts[6]

            # Instantiate influx client
            client = InfluxDBClient(db_host, db_port, db_user, db_pass, db_name)
            # Ensure the database exists or create it
            if db_name not in [db['name'] for db in client.get_list_database()]:
                client.create_database(db_name)

            # Create json
            json_body = [
                {
                    "measurement": "latency",
                    "tags": {
                        "url": url
                    },
                    "fields": {
                        "ping": ping
                    }
                }
            ]
            print(json_body)
            client.switch_database(db_name)
            client.write_points(json_body)
            # client.close()
    except sp.CalledProcessError as e:
        print(f"Error executing fping: {e}")
        print(f"Stderr: {e.stderr}")
        return None

# Run it
get_fping_results(targets)
