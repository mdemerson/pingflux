#!/usr/bin/env python3
import yaml #pip install pyaml
import subprocess as sp
from influxdb import InfluxDBClient

# Load our config
def load_config():
    """
    Load configuration from config.yaml file and extract database and host settings.

    Reads the YAML configuration file and extracts InfluxDB connection parameters
    and host addresses for monitoring targets.

    Returns:
        list: A list containing [db_host, db_port, db_name, db_user, db_pass, targets]
              where targets is a list of host addresses from the config file.
              Returns None if file is not found or YAML parsing fails.

    Raises:
        Prints error messages to stdout for FileNotFoundError and YAMLError,
        but does not raise exceptions.

    Expected config.yaml structure:
        influxdb:
            host: <database_host>
            port: <database_port>
            dbname: <database_name>
            dbuser: <database_username>
            dbpass: <database_password>
        hosts:
            - hostaddress: <host1_address>
            - hostaddress: <host2_address>
            ...
    """
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            db_host = config['influxdb']['host']
            db_port = config['influxdb']['port']
            db_name = config['influxdb']['dbname']
            db_user = config['influxdb']['dbuser']
            db_pass = config['influxdb']['dbpass']
            targets = []
            for host in config['hosts']:
                targets.append(host['hostaddress'])
            return [db_host, db_port, db_name, db_user, db_pass, targets]
    except FileNotFoundError:
        print("Error: config.yaml not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")

def ping_hosts_and_return_results(targets):
    """
    Execute fping command against target hosts and yield ping results.

    Uses fping to continuously ping a list of target hosts with specific options:
    - -D: Add timestamps to output
    - -b 56: Set packet size to 56 bytes
    - -l: Loop indefinitely (continuous pinging)
    - -r 0: Set retry count to 0
    - -p 1000: Set interval between pings to 1000ms

    Args:
        targets (list): List of host addresses/URLs to ping

    Yields:
        tuple: (url, ping_time) where ping_time is float in ms or None for timeouts

    Raises:
        subprocess.CalledProcessError: If fping command fails
    """
    command = ['fping', '-D', '-b', '56', '-l', '-r', '0', '-p', '1000'] + targets
    print(targets)
    try:
        process = sp.Popen(
            command,
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        print(f"running command: {' '.join(command)}")
        print("--- output ---")

        for line in process.stdout:
            parts = line.strip().split()
            if len(parts) >= 4:  # Ensure we have enough parts
                url = parts[1]
                if parts[4] == "timed":
                    ping = None
                else:
                    print("parts 6")
                    ping = parts[6]  # Convert to float for proper numeric handling

                yield url, ping

    except sp.CalledProcessError as e:
        print(f"Error executing fping: {e}")
        print(f"Stderr: {e.stderr}")
        raise


def create_json(url, ping):
    """
    Create InfluxDB JSON data point for ping measurement.

    Args:
        url (str): Target host URL/address
        ping (float or None): Ping time in milliseconds, None for timeouts

    Returns:
        list: InfluxDB JSON data point format
    """
    return [
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

def setup_influxdb_client(db_host, db_port, db_user, db_pass, db_name):
    """
    Setup and configure InfluxDB client with database creation if needed.

    Args:
        db_host (str): InfluxDB host address
        db_port (int): InfluxDB port number
        db_user (str): InfluxDB username
        db_pass (str): InfluxDB password
        db_name (str): InfluxDB database name

    Returns:
        InfluxDBClient: Configured client with database selected
    """
    client = InfluxDBClient(db_host, db_port, db_user, db_pass, db_name)

    # Ensure the database exists or create it
    if db_name not in [db['name'] for db in client.get_list_database()]:
        client.create_database(db_name)

    client.switch_database(db_name)
    return client


def main_ping_loop():
    """
    Main function that orchestrates the ping monitoring and data storage.

    Loads configuration, sets up database connection, and continuously
    processes ping results from fping command.
    """
    # Get info from config
    config_data = load_config()
    if not config_data:
        print("Failed to load configuration")
        return

    db_host, db_port, db_name, db_user, db_pass, targets = config_data

    # Setup InfluxDB client
    client = setup_influxdb_client(db_host, db_port, db_user, db_pass, db_name)

    try:
        # Process ping results continuously
        for url, ping in ping_hosts_and_return_results(targets):
            json_data = create_json(url, ping)
            client.write_points(json_data)

    except KeyboardInterrupt:
        print("\nStopping ping monitoring...")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        client.close()

# Run it
if __name__ == "__main__":
    main_ping_loop()
